import os
import json
import base64
import requests
from io import BytesIO
from typing import Optional
from PIL import Image


class ComfyUIFaceSwapAPI:
    """
    API client for ComfyUI face swap + cartoon stylization workflow.
    Optimized for high-volume processing (10,000+ images).
    """
    
    def __init__(self, comfyui_url: str = "http://127.0.0.1:8188"):
        """
        Initialize ComfyUI API client.
        
        Args:
            comfyui_url: Base URL of ComfyUI server (local or RunPod endpoint)
        """
        self.base_url = comfyui_url.rstrip('/')
        self.client_id = "desk-standee-api"
        
    def load_image_as_base64(self, image_path: str) -> str:
        """Convert local image to base64 string."""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def upload_image(self, image_path: str) -> dict:
        """
        Upload image to ComfyUI server.
        
        Args:
            image_path: Path to local image file
            
        Returns:
            dict with 'name' and 'subfolder' keys
        """
        with open(image_path, 'rb') as f:
            files = {'image': (os.path.basename(image_path), f, 'image/png')}
            response = requests.post(f"{self.base_url}/upload/image", files=files)
            response.raise_for_status()
            return response.json()
    
    def queue_prompt(self, workflow: dict) -> str:
        """
        Queue a workflow for execution.
        
        Args:
            workflow: ComfyUI workflow JSON
            
        Returns:
            prompt_id for tracking execution
        """
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        response = requests.post(f"{self.base_url}/prompt", json=payload)
        response.raise_for_status()
        return response.json()['prompt_id']
    
    def get_history(self, prompt_id: str) -> dict:
        """Get execution history for a prompt."""
        response = requests.get(f"{self.base_url}/history/{prompt_id}")
        response.raise_for_status()
        return response.json()
    
    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Download generated image from ComfyUI server."""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        response = requests.get(f"{self.base_url}/view", params=params)
        response.raise_for_status()
        return response.content
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> dict:
        """
        Poll for workflow completion.
        
        Args:
            prompt_id: ID returned from queue_prompt
            timeout: Maximum wait time in seconds
            
        Returns:
            History dict with output information
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id]
            time.sleep(1)
        
        raise TimeoutError(f"Workflow did not complete within {timeout} seconds")
    
    def create_workflow(
        self,
        source_face_image: str,
        target_body_image: str,
        style_strength: float = 0.8,
        cartoon_style: str = "illustration"
    ) -> dict:
        """
        Create ComfyUI workflow for face swap + cartoon stylization.
        
        Args:
            source_face_image: Uploaded image name (from upload_image)
            target_body_image: Uploaded image name (from upload_image)
            style_strength: Style transfer strength (0.0-1.0)
            cartoon_style: Style descriptor for prompting
            
        Returns:
            ComfyUI workflow JSON
        """
        workflow = {
            "1": {
                "inputs": {
                    "image": source_face_image,
                    "upload": "image"
                },
                "class_type": "LoadImage",
                "_meta": {"title": "Load Source Face"}
            },
            "2": {
                "inputs": {
                    "image": target_body_image,
                    "upload": "image"
                },
                "class_type": "LoadImage",
                "_meta": {"title": "Load Target Body"}
            },
            "3": {
                "inputs": {
                    "provider": "CPU"
                },
                "class_type": "InstantIDModelLoader",
                "_meta": {"title": "Load InstantID Model"}
            },
            "4": {
                "inputs": {
                    "instantid": ["3", 0],
                    "insightface": "CPU",
                    "control_net_name": "diffusion_pytorch_model.safetensors"
                },
                "class_type": "InstantIDFaceAnalysis",
                "_meta": {"title": "Analyze Source Face"}
            },
            "5": {
                "inputs": {
                    "face_analysis": ["4", 0],
                    "image": ["1", 0]
                },
                "class_type": "InstantIDFaceEmbedding",
                "_meta": {"title": "Extract Face Embedding"}
            },
            "6": {
                "inputs": {
                    "ckpt_name": "realisticVisionV60B1_v51VAE.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Base Model"}
            },
            "7": {
                "inputs": {
                    "text": f"professional {cartoon_style} style portrait, doctor with stethoscope, white coat, clean background, high quality, detailed face",
                    "clip": ["6", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Positive Prompt"}
            },
            "8": {
                "inputs": {
                    "text": "realistic photo, photograph, low quality, blurry, distorted face, multiple faces",
                    "clip": ["6", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "Negative Prompt"}
            },
            "9": {
                "inputs": {
                    "seed": int(os.urandom(4).hex(), 16) % (2**32),
                    "steps": 25,
                    "cfg": 7.5,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 0.85,
                    "model": ["6", 0],
                    "positive": ["7", 0],
                    "negative": ["8", 0],
                    "latent_image": ["10", 0],
                    "face_embedding": ["5", 0],
                    "ip_adapter_strength": style_strength
                },
                "class_type": "KSamplerAdvanced",
                "_meta": {"title": "Generate Image"}
            },
            "10": {
                "inputs": {
                    "width": 512,
                    "height": 768,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Create Latent"}
            },
            "11": {
                "inputs": {
                    "samples": ["9", 0],
                    "vae": ["6", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "Decode Latent"}
            },
            "12": {
                "inputs": {
                    "filename_prefix": "desk_standee",
                    "images": ["11", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Output"}
            }
        }
        return workflow
    
    def generate_face_swap(
        self,
        source_face_path: str,
        target_body_path: str,
        output_path: Optional[str] = None,
        style_strength: float = 0.8,
        cartoon_style: str = "illustration"
    ) -> bytes:
        """
        Complete face swap + stylization pipeline.
        
        Args:
            source_face_path: Path to source face image
            target_body_path: Path to target body/style reference
            output_path: Optional path to save output image
            style_strength: Style transfer strength (0.0-1.0)
            cartoon_style: Style descriptor
            
        Returns:
            Generated image as bytes
        """
        # Upload images
        print("Uploading source face...")
        source_upload = self.upload_image(source_face_path)
        
        print("Uploading target body...")
        target_upload = self.upload_image(target_body_path)
        
        # Create workflow
        print("Creating workflow...")
        workflow = self.create_workflow(
            source_face_image=source_upload['name'],
            target_body_image=target_upload['name'],
            style_strength=style_strength,
            cartoon_style=cartoon_style
        )
        
        # Queue and execute
        print("Queueing workflow...")
        prompt_id = self.queue_prompt(workflow)
        
        print(f"Waiting for completion (prompt_id: {prompt_id})...")
        history = self.wait_for_completion(prompt_id)
        
        # Extract output image
        outputs = history['outputs']
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                for img_info in node_output['images']:
                    image_data = self.get_image(
                        img_info['filename'],
                        img_info.get('subfolder', ''),
                        img_info.get('type', 'output')
                    )
                    
                    if output_path:
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        print(f"Saved to {output_path}")
                    
                    return image_data
        
        raise RuntimeError("No output image found in workflow results")


def main():
    """Example usage."""
    # Initialize API (use RunPod endpoint URL when deployed)
    api = ComfyUIFaceSwapAPI(comfyui_url="http://127.0.0.1:8188")
    
    # Generate face swap
    result = api.generate_face_swap(
        source_face_path="examples/Source Photo 1.png",
        target_body_path="examples/Style Reference.png",
        output_path="output.png",
        style_strength=0.85,
        cartoon_style="professional illustration"
    )
    
    print(f"Generated image: {len(result)} bytes")


if __name__ == "__main__":
    main()
