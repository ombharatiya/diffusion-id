import os
import time
import concurrent.futures
from pathlib import Path
from typing import List, Tuple
from comfyui_api import ComfyUIFaceSwapAPI


class BatchFaceSwapProcessor:
    """
    High-volume batch processor for face swap operations.
    Optimized for 10,000+ images with parallel processing.
    """
    
    def __init__(
        self,
        comfyui_url: str = "http://127.0.0.1:8188",
        max_workers: int = 4,
        retry_attempts: int = 3
    ):
        """
        Initialize batch processor.
        
        Args:
            comfyui_url: ComfyUI server URL (RunPod endpoint)
            max_workers: Number of parallel workers
            retry_attempts: Number of retries for failed images
        """
        self.api = ComfyUIFaceSwapAPI(comfyui_url)
        self.max_workers = max_workers
        self.retry_attempts = retry_attempts
        
    def process_single(
        self,
        source_face: str,
        target_body: str,
        output_path: str,
        style_strength: float = 0.85
    ) -> Tuple[bool, str, str]:
        """
        Process a single face swap with retry logic.
        
        Returns:
            (success, source_path, output_path or error_message)
        """
        for attempt in range(self.retry_attempts):
            try:
                self.api.generate_face_swap(
                    source_face_path=source_face,
                    target_body_path=target_body,
                    output_path=output_path,
                    style_strength=style_strength,
                    cartoon_style="professional illustration"
                )
                return (True, source_face, output_path)
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    return (False, source_face, str(e))
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return (False, source_face, "Max retries exceeded")
    
    def process_batch(
        self,
        source_faces: List[str],
        target_body: str,
        output_dir: str,
        style_strength: float = 0.85,
        progress_callback=None
    ) -> dict:
        """
        Process multiple face swaps in parallel.
        
        Args:
            source_faces: List of source face image paths
            target_body: Single target body/style reference
            output_dir: Directory to save outputs
            style_strength: Style transfer strength
            progress_callback: Optional callback(completed, total, success, failed)
            
        Returns:
            dict with 'successful', 'failed', 'total_time' keys
        """
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            'successful': [],
            'failed': [],
            'total_time': 0
        }
        
        start_time = time.time()
        completed = 0
        
        # Prepare tasks
        tasks = []
        for source_face in source_faces:
            filename = Path(source_face).stem
            output_path = os.path.join(output_dir, f"{filename}_output.png")
            tasks.append((source_face, target_body, output_path, style_strength))
        
        # Process in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.process_single, *task)
                for task in tasks
            ]
            
            for future in concurrent.futures.as_completed(futures):
                success, source, result = future.result()
                completed += 1
                
                if success:
                    results['successful'].append({'source': source, 'output': result})
                else:
                    results['failed'].append({'source': source, 'error': result})
                
                if progress_callback:
                    progress_callback(
                        completed,
                        len(tasks),
                        len(results['successful']),
                        len(results['failed'])
                    )
        
        results['total_time'] = time.time() - start_time
        return results
    
    def estimate_cost(
        self,
        num_images: int,
        gpu_type: str = "RTX 4090",
        avg_time_per_image: float = 8.0
    ) -> dict:
        """
        Estimate processing cost for RunPod deployment.
        
        Args:
            num_images: Number of images to process
            gpu_type: GPU type (affects pricing)
            avg_time_per_image: Average processing time in seconds
            
        Returns:
            dict with cost breakdown
        """
        # RunPod pricing (approximate, as of 2024)
        gpu_prices = {
            "RTX 4090": 0.69,      # $/hour
            "RTX 3090": 0.44,
            "A40": 0.79,
            "A100 40GB": 1.89,
            "A100 80GB": 2.49
        }
        
        hourly_rate = gpu_prices.get(gpu_type, 0.69)
        total_seconds = num_images * avg_time_per_image
        total_hours = total_seconds / 3600
        total_cost = total_hours * hourly_rate
        cost_per_image = total_cost / num_images
        
        return {
            'num_images': num_images,
            'gpu_type': gpu_type,
            'estimated_hours': round(total_hours, 2),
            'hourly_rate': hourly_rate,
            'total_cost': round(total_cost, 2),
            'cost_per_image': round(cost_per_image, 4),
            'avg_time_per_image': avg_time_per_image
        }


def progress_printer(completed, total, success, failed):
    """Simple progress callback."""
    print(f"Progress: {completed}/{total} | Success: {success} | Failed: {failed}")


def main():
    """Example batch processing."""
    processor = BatchFaceSwapProcessor(
        comfyui_url="http://127.0.0.1:8188",
        max_workers=4
    )
    
    # Example: Process all source photos with same target body
    source_faces = [
        "examples/Source Photo 1.png",
        "examples/Source Photo 2.png",
        "examples/Source Photo 3.png"
    ]
    
    target_body = "examples/Style Reference.png"
    output_dir = "outputs"
    
    print("Starting batch processing...")
    results = processor.process_batch(
        source_faces=source_faces,
        target_body=target_body,
        output_dir=output_dir,
        progress_callback=progress_printer
    )
    
    print("\n=== Batch Processing Complete ===")
    print(f"Successful: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Total time: {results['total_time']:.2f} seconds")
    print(f"Average time per image: {results['total_time']/len(source_faces):.2f} seconds")
    
    # Cost estimation for 10,000 images
    print("\n=== Cost Estimation for 10,000 Images ===")
    cost_estimate = processor.estimate_cost(10000, gpu_type="RTX 4090")
    for key, value in cost_estimate.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
