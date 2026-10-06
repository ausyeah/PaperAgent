import textwrap
from paperagent.models import PaperProject, ONNXExportBundle

class ONNXExportGenerator:
    """Generates ONNX and TensorRT compilation script bundles."""

    def generate_export_bundle(
        self, project: PaperProject, opset_version: int = 17
    ) -> ONNXExportBundle:
        """
        Synthesizes PyTorch to ONNX export and TensorRT compilation scripts.
        """
        model_name = project.id.replace("-", "_").lower()
        if not model_name:
            model_name = "model"

        onnx_export_script_py = textwrap.dedent(f"""\
            import torch
            import torch.onnx
            from model import Model # User needs to replace with actual model import

            def export_to_onnx(model, save_path="model.onnx", opset_version={opset_version}):
                model.eval()
                # Dummy input (e.g., for language models: batch_size=1, seq_length=128)
                dummy_input = torch.randint(0, 1000, (1, 128), dtype=torch.long)
                
                # Export with dynamic axes for variable batch size and sequence length
                torch.onnx.export(
                    model,
                    dummy_input,
                    save_path,
                    export_params=True,
                    opset_version=opset_version,
                    do_constant_folding=True,
                    input_names=['input_ids'],
                    output_names=['logits'],
                    dynamic_axes={{
                        'input_ids': {{0: 'batch_size', 1: 'sequence_length'}},
                        'logits': {{0: 'batch_size', 1: 'sequence_length'}}
                    }}
                )
                print(f"Model successfully exported to {{save_path}}")

            if __name__ == "__main__":
                model = Model() # User needs to instantiate actual model
                export_to_onnx(model)
        """)

        tensorrt_builder_script_py = textwrap.dedent("""\
            import tensorrt as trt
            import os

            TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

            def build_engine(onnx_file_path, engine_file_path, fp16_mode=True, int8_mode=False):
                builder = trt.Builder(TRT_LOGGER)
                network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
                config = builder.create_builder_config()
                
                # Set memory pool limit (e.g., 2GB)
                config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 31)

                if fp16_mode and builder.platform_has_fast_fp16:
                    config.set_flag(trt.BuilderFlag.FP16)
                if int8_mode and builder.platform_has_fast_int8:
                    config.set_flag(trt.BuilderFlag.INT8)

                parser = trt.OnnxParser(network, TRT_LOGGER)
                if not os.path.exists(onnx_file_path):
                    print(f"ONNX file {onnx_file_path} not found.")
                    return None

                with open(onnx_file_path, "rb") as model:
                    if not parser.parse(model.read()):
                        print("Failed to parse ONNX file.")
                        for error in range(parser.num_errors):
                            print(parser.get_error(error))
                        return None
                
                print("Building TensorRT engine. This may take a while...")
                engine_bytes = builder.build_serialized_network(network, config)
                if engine_bytes is None:
                    print("Failed to create engine.")
                    return None
                    
                with open(engine_file_path, "wb") as f:
                    f.write(engine_bytes)
                print(f"Engine built successfully and saved to {engine_file_path}")
                return engine_bytes

            if __name__ == "__main__":
                build_engine("model.onnx", "model.engine")
        """)

        simplification_instructions = textwrap.dedent("""\
            # To simplify the ONNX model before TensorRT compilation, install onnxsim:
            # pip install onnxsim
            #
            # Then run the following command in your terminal:
            # onnxsim model.onnx model_sim.onnx
            #
            # After simplification, update the TensorRT script to use `model_sim.onnx`.
        """)

        return ONNXExportBundle(
            model_name=model_name,
            onnx_export_script_py=onnx_export_script_py,
            tensorrt_builder_script_py=tensorrt_builder_script_py,
            opset_version=opset_version,
            simplification_instructions=simplification_instructions,
        )