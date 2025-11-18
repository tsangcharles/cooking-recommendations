from PIL import Image
import os

class ImageStitcher:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def clean_output_dir(self):
        """Delete all files in the output directory"""
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        
    def stitch_images(self, image_files, output_filename="complete_flyer.jpg"):
        """Stitch multiple images into a grid layout (somewhat square)"""
        if not image_files:
            print("No images to stitch!")
            return None
            
        try:
            print("Cleaning output directory...")
            self.clean_output_dir()
            print()
            
            print(f"Stitching {len(image_files)} images into a grid...")
            
            # Sort files to ensure consistent order
            image_files = sorted(image_files)
            
            # Open all images
            images = [Image.open(img) for img in image_files]
            
            num_images = len(images)
            
            # Calculate grid dimensions (try to make it somewhat square)
            # Find factors close to square root
            import math
            cols = math.ceil(math.sqrt(num_images))
            rows = math.ceil(num_images / cols)
            
            print(f"Creating {rows}x{cols} grid for {num_images} images")
            
            # Get max dimensions for each cell
            max_width = max(img.width for img in images)
            max_height = max(img.height for img in images)
            
            # Calculate total canvas size
            canvas_width = max_width * cols
            canvas_height = max_height * rows
            
            print(f"Creating stitched image: {canvas_width}x{canvas_height}px")
            
            # Create a new image with white background
            stitched_image = Image.new('RGB', (canvas_width, canvas_height), 'white')
            
            # Paste each image in grid
            for idx, img in enumerate(images):
                row = idx // cols
                col = idx % cols
                
                x_pos = col * max_width
                y_pos = row * max_height
                
                # Center the image in its cell if it's smaller
                x_offset = (max_width - img.width) // 2
                y_offset = (max_height - img.height) // 2
                
                print(f"Adding image {idx+1}/{num_images} at position ({row},{col}) -> ({x_pos + x_offset}, {y_pos + y_offset})")
                stitched_image.paste(img, (x_pos + x_offset, y_pos + y_offset))
            
            # Save the result
            output_path = os.path.join(self.output_dir, output_filename)
            stitched_image.save(output_path, 'JPEG', quality=95)
            print(f"Stitched image saved to: {output_path}")
            print(f"Grid layout: {rows} rows × {cols} columns")
            
            # Close all images
            for img in images:
                img.close()
                
            return output_path
            
        except Exception as e:
            print(f"Error stitching images: {e}")
            import traceback
            traceback.print_exc()
            return None
