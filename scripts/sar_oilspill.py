# import os
# import cv2
# import numpy as np
# import torch
# import torch.nn as nn
# import torchvision.transforms as transforms
# import matplotlib.pyplot as plt
# import skimage.feature as feature
# import scipy.stats as stats
# import math
# import torchvision.models as models
# import warnings
# import torch
# from lime import lime_image
# from skimage.segmentation import mark_boundaries
# import matplotlib.pyplot as plt
# import numpy as np
# import cv2
# import io
# import base64
# from PIL import Image


# warnings.filterwarnings("ignore")

# class DualAttentionUNet(nn.Module):
#     def __init__(self, in_channels=1, out_channels=1):
#         super(DualAttentionUNet, self).__init__()
        
#         # Encoder (Downsampling)
#         self.enc1 = self._conv_block(in_channels, 64)
#         self.enc2 = self._conv_block(64, 128)
#         self.enc3 = self._conv_block(128, 256)
#         self.enc4 = self._conv_block(256, 512)
        
#         # Bridge
#         self.bridge = self._conv_block(512, 1024)
        
#         # Decoder (Upsampling) with Dual Attention
#         self.upconv4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
#         self.dec4 = self._conv_block(1024, 512)
        
#         self.upconv3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
#         self.dec3 = self._conv_block(512, 256)
        
#         self.upconv2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
#         self.dec2 = self._conv_block(256, 128)
        
#         self.upconv1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
#         self.dec1 = self._conv_block(128, 64)
        
#         # Final Convolutional Layer
#         self.final_conv = nn.Conv2d(64, out_channels, kernel_size=1)
        
#         # Spatial Attention Module
#         self.spatial_attention = nn.Sequential(
#             nn.Conv2d(2, 1, kernel_size=7, padding=3),
#             nn.Sigmoid()
#         )
        
#         # Channel Attention Module
#         self.channel_attention = nn.Sequential(
#             nn.AdaptiveAvgPool2d(1),
#             nn.Conv2d(1024, 1024 // 16, kernel_size=1),
#             nn.ReLU(),
#             nn.Conv2d(1024 // 16, 1024, kernel_size=1),
#             nn.Sigmoid()
#         )
    
#     def _conv_block(self, in_channels, out_channels):
#         return nn.Sequential(
#             nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
#             nn.BatchNorm2d(out_channels),
#             nn.ReLU(inplace=True),
#             nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
#             nn.BatchNorm2d(out_channels),
#             nn.ReLU(inplace=True)
#         )
    
#     def forward(self, x):
#         # Encoder
#         enc1 = self.enc1(x)
#         enc2 = self.enc2(nn.MaxPool2d(2)(enc1))
#         enc3 = self.enc3(nn.MaxPool2d(2)(enc2))
#         enc4 = self.enc4(nn.MaxPool2d(2)(enc3))
        
#         # Bridge
#         bridge = self.bridge(nn.MaxPool2d(2)(enc4))
        
#         # Channel Attention
#         channel_attn = self.channel_attention(bridge)
#         bridge = bridge * channel_attn
        
#         # Decoder with Spatial Attention
#         up4 = self.upconv4(bridge)
        
#         # Spatial Attention
#         avg_out = torch.mean(up4, dim=1, keepdim=True)
#         max_out, _ = torch.max(up4, dim=1, keepdim=True)
#         spatial_attn = torch.cat([avg_out, max_out], dim=1)
#         spatial_attn = self.spatial_attention(spatial_attn)
#         up4 = up4 * spatial_attn
        
#         dec4 = self.dec4(torch.cat([up4, enc4], dim=1))
        
#         up3 = self.upconv3(dec4)
#         dec3 = self.dec3(torch.cat([up3, enc3], dim=1))
        
#         up2 = self.upconv2(dec3)
#         dec2 = self.dec2(torch.cat([up2, enc2], dim=1))
        
#         up1 = self.upconv1(dec2)
#         dec1 = self.dec1(torch.cat([up1, enc1], dim=1))
        
#         return self.final_conv(dec1)

# def load_resnet_model(
#     model_path: str, 
#     device: str = 'cuda', 
#     num_classes: int = 2 
# ) -> nn.Module:

#     try:
#         # Initialize base ResNet50 model
#         model = models.resnet50(pretrained=False)
        
#         # Modify the final fully connected layer
#         num_features = model.fc.in_features
#         model.fc = nn.Linear(num_features, num_classes)
        
#         # Load pre-trained weights
#         if model_path and os.path.exists(model_path):
#             try:
#                 # Attempt to load state dict
#                 state_dict = torch.load(model_path, map_location=device)
                
#                 # Handle different state dict formats
#                 if 'model_state_dict' in state_dict:
#                     state_dict = state_dict['model_state_dict']
                
#                 # Load the state dictionary
#                 model.load_state_dict(state_dict)
#                 print(f"Successfully loaded model weights from {model_path}")
            
#             except Exception as load_error:
#                 print(f"Error loading model weights: {load_error}")
#                 print("Initializing model with random weights")
        
#         # Move model to specified device
#         model = model.to(device)
        
#         # Set model to evaluation mode
#         model.eval()
        
#         return model
    
#     except Exception as e:
#         print(f"Critical error in model loading: {e}")
#         raise

# def preprocess_image_for_inference(image_path, device='cuda'):
#     """
#     Comprehensive preprocessing function for SAR image inference
#     """
#     # Read image in grayscale
#     sar_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
#     sar_image=cv2.resize(sar_image,(400,400))
    
#     # Normalize image intensities
#     normalized_image = ((sar_image - np.min(sar_image)) / 
#                         (np.max(sar_image) - np.min(sar_image)) * 255).astype(np.uint8)
    
#     # Multi-looking (blurring)
#     look_factor = 2
#     multilooked_image = cv2.blur(normalized_image, (look_factor, look_factor))
    
#     # Denoising
#     filtered_image = cv2.fastNlMeansDenoising(multilooked_image.astype(np.uint8), 
#                                             None, h=10, 
#                                             templateWindowSize=7, 
#                                             searchWindowSize=21)
    
#     # Convert to decibel scale
#     db_image = 10 * np.log10(filtered_image + 1e-10)
#     db_image_uint8 = np.clip(db_image, 0, 255).astype(np.uint8)

    
    
#     # Create transform
#     transform = transforms.Compose([
#         transforms.ToPILImage(),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.5], std=[0.5])
#     ])
    
#     # Apply transforms
#     image_tensor = transform(db_image_uint8)
    
#     # Move to specified device
#     preprocessed_image = image_tensor.to(device)
    
#     return preprocessed_image

# def load_model(model_path, device='cuda'):
#     """
#     Load trained model weights
#     """
#     model = DualAttentionUNet()
#     model.load_state_dict(torch.load(model_path, map_location=device))
#     model = model.to(device)
#     model.eval()
#     return model

# def inference(model, image_path, device='cuda'):
#     """
#     Run model inference with comprehensive preprocessing
#     """
#     # Ensure model is on the correct device
#     model = model.to(device)
    
#     # Preprocess the image 
#     preprocessed_image = preprocess_image_for_inference(image_path, device)
    
#     # Add batch dimension
#     preprocessed_image = preprocessed_image.unsqueeze(0)
    
#     # Set model to evaluation mode
#     model.eval()
    
#     # Disable gradient computation
#     with torch.no_grad():
#         # Get model prediction
#         output = model(preprocessed_image)
        
#         # Apply sigmoid and thresholding
#         prediction = torch.sigmoid(output)
#         prediction = (prediction > 0.5).float()
    
#     # Move to CPU and remove batch dimension
#     return prediction.squeeze(0).cpu()

# def tensor_to_numpy(tensor):
#     """
#     Safely convert a tensor to numpy array
#     """
#     if isinstance(tensor, torch.Tensor):
#         # Detach from computation graph and move to CPU
#         tensor = tensor.detach().cpu()
        
#         # Remove singleton dimensions
#         while tensor.dim() > 2:
#             tensor = tensor.squeeze(0)
        
#         # Convert to numpy
#         return tensor.numpy()
    
#     return tensor

# def apply_morphological_operations(binary_mask):
#     # Ensure binary mask is binary
#     binary_mask = (binary_mask > 0).astype(np.uint8)
    
#     # Kernels for morphological operations
#     kernel_3x3 = np.ones((3, 3), np.uint8)
    
#     # Morphological operations
#     closed_masks = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel_3x3)
#     return closed_masks

# def apply_morphological_operations(binary_mask):
#     # Ensure binary mask is binary
#     binary_mask = (binary_mask > 0).astype(np.uint8)
    
#     # Kernels for morphological operations
#     kernel_3x3 = np.ones((3, 3), np.uint8)
#     kernel_5x5 = np.ones((5, 5), np.uint8)
    
#     # Morphological operations
#     closed_masks = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel_3x3)
#     return closed_masks

# def _create_overlay(base_image, mask):
#     # Ensure base image is in color
#     if len(base_image.shape) == 2:
#         overlay = cv2.cvtColor(base_image, cv2.COLOR_GRAY2RGB)
#     else:
#         overlay = base_image.copy()
    
#     overlay[mask > 0] = [255, 255, 0]
    
#     return overlay

# # Prediction Pipeline
# def predict(model, image, transform,device):
#     model.eval()
#     # image=cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     image = transform(image).unsqueeze(0)  # Add batch dimension

#     image = image.to(device)
#     with torch.no_grad():
#         outputs = model(image)
#         _, predicted_class = torch.max(outputs, 1)
#     return predicted_class.item()

# # Convert to 3-channel since ResNet expects 3-channel inputs
# def to_3_channels(image):
#     return np.stack([image] * 3, axis=-1)


# def oilspill_pipeline(base64_image, model_unet_path='models/sar_models/best_model.pth', 
#             model_resnet_path='models/sar_models/best_resnet50_model.pth', 
#             device='cuda'):
    
#     # Decode base64 image
#     image_bytes = base64.b64decode(base64_image)
#     image_np = np.array(Image.open(io.BytesIO(image_bytes)))
    
#     # Convert to grayscale if color image
#     if len(image_np.shape) == 3:
#         original_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
#     else:
#         original_image = image_np

#     # Rest of your existing pipeline code remains the same
#     model_unet = load_model(model_unet_path, device)
#     model_resnet = load_resnet_model(model_resnet_path, device)
    
#     top_labels = 2
#     num_samples = 1000
                
#     original_image = cv2.resize(original_image, (400, 400))

#     # Normalize original image
#     original_image_normalized = ((original_image - original_image.min()) / 
#                                 (original_image.max() - original_image.min()) * 255).astype(np.uint8)

#     # Temporary image save for inference (if needed)
#     temp_image_path = 'temp_image.png'
#     cv2.imwrite(temp_image_path, original_image)

#     # Run inference on the image
#     prediction_mask = inference(model_unet, temp_image_path, device)
    
#     # Remove temporary image
#     import os
#     os.remove(temp_image_path)

#     # Convert prediction mask to numpy
#     prediction_mask_np = tensor_to_numpy(prediction_mask)
#     prediction_mask_np = (prediction_mask_np * 255).astype(np.uint8)

#     # Visualize original and morphological results
#     closed_mask = apply_morphological_operations(prediction_mask_np)

#     # Save the overlayed result
#     overlay_image = _create_overlay(original_image_normalized, closed_mask)
    
#     transform = transforms.Compose([
#     transforms.Lambda(to_3_channels),  # Convert grayscale to 3 channels
#     transforms.ToPILImage(),           # Convert numpy image to PIL image
#     transforms.Resize((224, 224)),     # Resize to fixed 224x224
#     transforms.ToTensor(),
#     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
#     ])
    
#     gray_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    
#     res_prediction = predict(model_resnet, gray_image, transform, device)
#     print(res_prediction)
    
#     # # Prepare image for LIME (3-channel, resized)
#     # lime_input_image = to_3_channels(gray_image)
#     # lime_input_image = cv2.resize(lime_input_image, (224, 224))
    
#     # def predict_proba(images):
#     #     from PIL import Image
#     #     transform = transforms.Compose([
#     #     transforms.Lambda(lambda x: Image.fromarray(x)),  # Convert numpy to PIL
#     #     transforms.Resize((224, 224)),     # Resize to fixed 224x224
#     #     transforms.ToTensor(),
#     #     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
#     #     ])
#     #     model_resnet.eval()

#     #     # Ensure images is a numpy array and has correct shape
#     #     if isinstance(images, list):
#     #         images = np.array(images)
        
#     #     # Process each image individually
#     #     processed_images = []
#     #     for img in images:
#     #         # Flatten the batch dimension if present
#     #         if img.ndim == 4:
#     #             for single_img in img:
#     #                 # Ensure uint8 and correct shape
#     #                 single_img = single_img.astype(np.uint8)
                    
#     #                 # Apply transform
#     #                 try:
#     #                     processed_img = transform(single_img)
#     #                     processed_images.append(processed_img)
#     #                 except Exception as e:
#     #                     raise
#     #         else:
#     #             # Ensure uint8 and correct shape
#     #             img = img.astype(np.uint8)
                
#     #             # Apply transform
#     #             try:
#     #                 processed_img = transform(img)
#     #                 processed_images.append(processed_img)
#     #             except Exception as e:
#     #                 raise
        
#     #     # Stack processed images
#     #     processed_images = torch.stack(processed_images).to(device)
        
#     #     with torch.no_grad():
#     #         outputs = model_resnet(processed_images)
#     #         probabilities = torch.softmax(outputs, dim=1)
        
#     #     return probabilities.cpu().numpy()

#     # # Initialize LIME explainer
#     # explainer = lime_image.LimeImageExplainer()

#     # # Generate LIME explanation
#     # explanation = explainer.explain_instance(
#     #     lime_input_image,
#     #     predict_proba,
#     #     top_labels=top_labels,
#     #     hide_color=0,
#     #     num_samples=num_samples
#     # )

#     # # Visualize explanation
#     # temp, mask = explanation.get_image_and_mask(
#     #     explanation.top_labels[0],
#     #     positive_only=True,
#     #     num_features=10,
#     #     hide_rest=False
#     # )
    
#     # lime_mask_resized = cv2.resize(mask.astype(np.uint8), (original_image.shape[1], original_image.shape[0]))
    
#     original_image_color = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)

    
#     # # Create LIME explanation overlay on original image
#     # lime_overlay = mark_boundaries(
#     #     original_image_color/ 255.0, 
#     #     lime_mask_resized, 
#     #     color=(1, 0, 0)  # Red boundaries
#     # )
    
#     # After creating the lime_overlay
#     def convert_to_base64(lime_overlay):
#         # Convert the numpy array to a PIL Image
#         pil_image = Image.fromarray((lime_overlay * 255).astype(np.uint8))
        
#         # Create a bytes buffer
#         buffer = io.BytesIO()
        
#         # Save the image to the buffer in PNG format
#         pil_image.save(buffer, format="PNG")
        
#         # Get the byte data from the buffer
#         image_bytes = buffer.getvalue()
        
#         # Encode the bytes to base64
#         base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        
#         return base64_encoded

#     # plt.subplot(133)
#     # plt.title('LIME Explanation')
#     # plt.imshow(lime_overlay)
#     # plt.axis('off')

#     # plt.tight_layout()
#     # plt.show()e

#     return {"Predicted Class":res_prediction,"Original Image":convert_to_base64(original_image_color),"SAR_mask":convert_to_base64(overlay_image)}#,"LIME Explanation":convert_to_base64(lime_overlay)}


# # def pipeline(image_path,model_unet_path='/home/yuvraj/Coding/sih/best_model.pth',model_resnet_path='/home/yuvraj/Coding/sih/best_resnet50_model.pth', device='cuda'):
    
# #     model_unet = load_model(model_unet_path, device)
# #     model_resnet=load_resnet_model(model_resnet_path,device)
    
# #     top_labels=2
# #     num_samples=1000
                
# #     original_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
# #     original_image=cv2.resize(original_image,(400,400))

# #     # Normalize original image
# #     original_image_normalized = ((original_image - original_image.min()) / 
# #                                 (original_image.max() - original_image.min()) * 255).astype(np.uint8)

# #     # Run inference on the image
# #     prediction_mask = inference(model_unet, image_path, device)
    
# #     # Convert prediction mask to numpy
# #     prediction_mask_np = tensor_to_numpy(prediction_mask)
# #     prediction_mask_np = (prediction_mask_np * 255).astype(np.uint8)

# #     # Visualize original and morphological results
# #     closed_mask = apply_morphological_operations(prediction_mask_np)

# #     # Save the overlayed result
# #     overlay_image = _create_overlay(original_image_normalized, closed_mask)
    
# #     transform = transforms.Compose([
# #     transforms.Lambda(to_3_channels),  # Convert grayscale to 3 channels
# #     transforms.ToPILImage(),           # Convert numpy image to PIL image
# #     transforms.Resize((224, 224)),     # Resize to fixed 224x224
# #     transforms.ToTensor(),
# #     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
# #     ])
    
# #     gray_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    
# #     res_prediction=predict(model_resnet,gray_image ,transform,device)
# #     print(res_prediction)
    
    
# #     # Prepare image for LIME (3-channel, resized)
# #     lime_input_image = to_3_channels(gray_image)
# #     lime_input_image = cv2.resize(lime_input_image, (224, 224))
    
# #     def predict_proba(images):
# #         from PIL import Image
# #         transform = transforms.Compose([
# #         transforms.Lambda(lambda x: Image.fromarray(x)),  # Convert numpy to PIL
# #         transforms.Resize((224, 224)),     # Resize to fixed 224x224
# #         transforms.ToTensor(),
# #         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
# #         ])
# #         model_resnet.eval()

# #         # Ensure images is a numpy array and has correct shape
# #         if isinstance(images, list):
# #             images = np.array(images)
        
# #         # Process each image individually
# #         processed_images = []
# #         for img in images:
# #             # Flatten the batch dimension if present
# #             if img.ndim == 4:
# #                 for single_img in img:
# #                     # Ensure uint8 and correct shape
# #                     single_img = single_img.astype(np.uint8)
                    
# #                     # Apply transform
# #                     try:
# #                         processed_img = transform(single_img)
# #                         processed_images.append(processed_img)
# #                     except Exception as e:
# #                         raise
# #             else:
# #                 # Ensure uint8 and correct shape
# #                 img = img.astype(np.uint8)
                
# #                 # Apply transform
# #                 try:
# #                     processed_img = transform(img)
# #                     processed_images.append(processed_img)
# #                 except Exception as e:
# #                     raise
        
# #         # Stack processed images
# #         processed_images = torch.stack(processed_images).to(device)
        
# #         with torch.no_grad():
# #             outputs = model_resnet(processed_images)
# #             probabilities = torch.softmax(outputs, dim=1)
        
# #         return probabilities.cpu().numpy()

# #     # Initialize LIME explainer
# #     explainer = lime_image.LimeImageExplainer()

# #     # Generate LIME explanation
# #     explanation = explainer.explain_instance(
# #         lime_input_image,
# #         predict_proba,
# #         top_labels=top_labels,
# #         hide_color=0,
# #         num_samples=num_samples
# #     )

# #     # Visualize explanation
# #     temp, mask = explanation.get_image_and_mask(
# #         explanation.top_labels[0],
# #         positive_only=True,
# #         num_features=10,
# #         hide_rest=False
# #     )
    
# #     lime_mask_resized = cv2.resize(mask.astype(np.uint8), (original_image.shape[1], original_image.shape[0]))
    
# #     original_image_color = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)

    
# #     # Create LIME explanation overlay on original image
# #     lime_overlay = mark_boundaries(
# #         original_image_color/ 255.0, 
# #         lime_mask_resized, 
# #         color=(1, 0, 0)  # Red boundaries
# #     )
    
# #     # After creating the lime_overlay
# #     def convert_to_base64(lime_overlay):
# #         # Convert the numpy array to a PIL Image
# #         pil_image = Image.fromarray((lime_overlay * 255).astype(np.uint8))
        
# #         # Create a bytes buffer
# #         buffer = io.BytesIO()
        
# #         # Save the image to the buffer in PNG format
# #         pil_image.save(buffer, format="PNG")
        
# #         # Get the byte data from the buffer
# #         image_bytes = buffer.getvalue()
        
# #         # Encode the bytes to base64
# #         base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        
# #         return base64_encoded

# #     plt.subplot(133)
# #     plt.title('LIME Explanation')
# #     plt.imshow(lime_overlay)
# #     plt.axis('off')

# #     plt.tight_layout()
# #     plt.show()

# #     return {"Predicted Class":res_prediction,"Original Image":convert_to_base64(original_image_color),"LIME Explanation":convert_to_base64(lime_overlay)}

# # if __name__ == "__main__":
# #     print(pipeline('/home/yuvraj/Coding/sih/data/oil.jpeg',device='cuda'))

import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import skimage.feature as feature
import scipy.stats as stats
import math
import torchvision.models as models
import warnings
import torch
from lime import lime_image
from skimage.segmentation import mark_boundaries
import matplotlib.pyplot as plt
import numpy as np
import cv2
import io
import base64
from PIL import Image


warnings.filterwarnings("ignore")

class DualAttentionUNet(nn.Module):
    def __init__(self, in_channels=1, out_channels=1):
        super(DualAttentionUNet, self).__init__()
        
        # Encoder (Downsampling)
        self.enc1 = self._conv_block(in_channels, 64)
        self.enc2 = self._conv_block(64, 128)
        self.enc3 = self._conv_block(128, 256)
        self.enc4 = self._conv_block(256, 512)
        
        # Bridge
        self.bridge = self._conv_block(512, 1024)
        
        # Decoder (Upsampling) with Dual Attention
        self.upconv4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = self._conv_block(1024, 512)
        
        self.upconv3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = self._conv_block(512, 256)
        
        self.upconv2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = self._conv_block(256, 128)
        
        self.upconv1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = self._conv_block(128, 64)
        
        # Final Convolutional Layer
        self.final_conv = nn.Conv2d(64, out_channels, kernel_size=1)
        
        # Spatial Attention Module
        self.spatial_attention = nn.Sequential(
            nn.Conv2d(2, 1, kernel_size=7, padding=3),
            nn.Sigmoid()
        )
        
        # Channel Attention Module
        self.channel_attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(1024, 1024 // 16, kernel_size=1),
            nn.ReLU(),
            nn.Conv2d(1024 // 16, 1024, kernel_size=1),
            nn.Sigmoid()
        )
    
    def _conv_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(nn.MaxPool2d(2)(enc1))
        enc3 = self.enc3(nn.MaxPool2d(2)(enc2))
        enc4 = self.enc4(nn.MaxPool2d(2)(enc3))
        
        # Bridge
        bridge = self.bridge(nn.MaxPool2d(2)(enc4))
        
        # Channel Attention
        channel_attn = self.channel_attention(bridge)
        bridge = bridge * channel_attn
        
        # Decoder with Spatial Attention
        up4 = self.upconv4(bridge)
        
        # Spatial Attention
        avg_out = torch.mean(up4, dim=1, keepdim=True)
        max_out, _ = torch.max(up4, dim=1, keepdim=True)
        spatial_attn = torch.cat([avg_out, max_out], dim=1)
        spatial_attn = self.spatial_attention(spatial_attn)
        up4 = up4 * spatial_attn
        
        dec4 = self.dec4(torch.cat([up4, enc4], dim=1))
        
        up3 = self.upconv3(dec4)
        dec3 = self.dec3(torch.cat([up3, enc3], dim=1))
        
        up2 = self.upconv2(dec3)
        dec2 = self.dec2(torch.cat([up2, enc2], dim=1))
        
        up1 = self.upconv1(dec2)
        dec1 = self.dec1(torch.cat([up1, enc1], dim=1))
        
        return self.final_conv(dec1)

def load_resnet_model(
    model_path: str, 
    device: str = 'cuda', 
    num_classes: int = 2 
) -> nn.Module:

    try:
        # Initialize base ResNet50 model
        model = models.resnet50(pretrained=False)
        
        # Modify the final fully connected layer
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, num_classes)
        
        # Load pre-trained weights
        if model_path and os.path.exists(model_path):
            try:
                # Attempt to load state dict
                state_dict = torch.load(model_path, map_location=device)
                
                # Handle different state dict formats
                if 'model_state_dict' in state_dict:
                    state_dict = state_dict['model_state_dict']
                
                # Load the state dictionary
                model.load_state_dict(state_dict)
                print(f"Successfully loaded model weights from {model_path}")
            
            except Exception as load_error:
                print(f"Error loading model weights: {load_error}")
                print("Initializing model with random weights")
        
        # Move model to specified device
        model = model.to(device)
        
        # Set model to evaluation mode
        model.eval()
        
        return model
    
    except Exception as e:
        print(f"Critical error in model loading: {e}")
        raise

def preprocess_image_for_inference(image_path, device='cuda'):

    # Read image in grayscale
    sar_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    sar_image=cv2.resize(sar_image,(400,400))
    
    # Normalize image intensities
    normalized_image = ((sar_image - np.min(sar_image)) / 
                        (np.max(sar_image) - np.min(sar_image)) * 255).astype(np.uint8)
    
    # Multi-looking (blurring)
    look_factor = 2
    multilooked_image = cv2.blur(normalized_image, (look_factor, look_factor))
    
    # Denoising
    filtered_image = cv2.fastNlMeansDenoising(multilooked_image.astype(np.uint8), 
                                            None, h=10, 
                                            templateWindowSize=7, 
                                            searchWindowSize=21)
    
    # Convert to decibel scale
    db_image = 10 * np.log10(filtered_image + 1e-10)
    db_image_uint8 = np.clip(db_image, 0, 255).astype(np.uint8)

    
    
    # Create transform
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])
    
    # Apply transforms
    image_tensor = transform(db_image_uint8)
    
    # Move to specified device
    preprocessed_image = image_tensor.to(device)
    
    return preprocessed_image

def load_model(model_path, device='cuda'):

    model = DualAttentionUNet()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model

def inference(model, image_path, device='cuda'):

    # Ensure model is on the correct device
    model = model.to(device)
    
    # Preprocess the image 
    preprocessed_image = preprocess_image_for_inference(image_path, device)
    
    # Add batch dimension
    preprocessed_image = preprocessed_image.unsqueeze(0)
    
    # Set model to evaluation mode
    model.eval()
    
    # Disable gradient computation
    with torch.no_grad():
        # Get model prediction
        output = model(preprocessed_image)
        
        # Apply sigmoid and thresholding
        prediction = torch.sigmoid(output)
        prediction = (prediction > 0.5).float()
    
    # Move to CPU and remove batch dimension
    return prediction.squeeze(0).cpu()

def tensor_to_numpy(tensor):

    if isinstance(tensor, torch.Tensor):
        # Detach from computation graph and move to CPU
        tensor = tensor.detach().cpu()
        
        # Remove singleton dimensions
        while tensor.dim() > 2:
            tensor = tensor.squeeze(0)
        
        # Convert to numpy
        return tensor.numpy()
    
    return tensor

def apply_morphological_operations(binary_mask):
    # Ensure binary mask is binary
    binary_mask = (binary_mask > 0).astype(np.uint8)
    
    # Kernels for morphological operations
    kernel_3x3 = np.ones((3, 3), np.uint8)
    
    # Morphological operations
    closed_masks = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel_3x3)
    return closed_masks

def apply_morphological_operations(binary_mask):
    # Ensure binary mask is binary
    binary_mask = (binary_mask > 0).astype(np.uint8)
    
    # Kernels for morphological operations
    kernel_3x3 = np.ones((3, 3), np.uint8)
    kernel_5x5 = np.ones((5, 5), np.uint8)
    
    # Morphological operations
    closed_masks = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel_3x3)
    return closed_masks

def _create_overlay(base_image, mask):
    # Ensure base image is in color
    if len(base_image.shape) == 2:
        overlay = cv2.cvtColor(base_image, cv2.COLOR_GRAY2RGB)
    else:
        overlay = base_image.copy()
    
    # Resize mask to match base image dimensions
    mask = cv2.resize(mask, (base_image.shape[1], base_image.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    overlay[mask > 0] = [255, 255, 0]
    
    return overlay


# Prediction Pipeline
def predict(model, image, transform,device):
    model.eval()
    # image=cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = transform(image).unsqueeze(0)  # Add batch dimension

    image = image.to(device)
    with torch.no_grad():
        outputs = model(image)
        _, predicted_class = torch.max(outputs, 1)
    return predicted_class.item()

# Convert to 3-channel since ResNet expects 3-channel inputs
def to_3_channels(image):
    return np.stack([image] * 3, axis=-1)


def oilspill_pipeline(base64_image, model_unet_path='/home/yuvraj/Coding/sih/best_model.pth', model_resnet_path='/home/yuvraj/Coding/sih/best_resnet50_model.pth', device='cuda'):
    
    # Decode base64 image
    image_bytes = base64.b64decode(base64_image)
    
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    
    # Decode image
    original_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    model_unet = load_model(model_unet_path, device)
    model_resnet = load_resnet_model(model_resnet_path, device)
    
    # Resize original image to 400x400
    original_image = cv2.resize(original_image, (400, 400))

    # Normalize original image
    original_image_normalized = ((original_image - original_image.min()) / 
                                (original_image.max() - original_image.min()) * 255).astype(np.uint8)

    # Apply Otsu's thresholding to create a binary mask
    _, binary_mask = cv2.threshold(original_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Invert the mask to make land cover (white parts) black and oil spills white
    inverted_mask = cv2.bitwise_not(binary_mask)

    # Create a light gray color (RGB)
    light_gray_color = np.array([110, 110, 110], dtype=np.uint8)

    # Create a result image initialized with light gray color
    result_image = np.full((400, 400), light_gray_color[0], dtype=np.uint8)

    # Apply the inverted mask to retain oil spill areas in the original image
    result_image[inverted_mask == 255] = original_image[inverted_mask == 255]

    # Temporary save path for the masked image (for UNet preprocessing)
    temp_masked_path = 'temp_masked_image.jpg'
    cv2.imwrite(temp_masked_path, result_image)

    preprocessed_image = preprocess_image_for_inference(temp_masked_path, device)

    
    # Run inference on the masked image
    prediction_mask = inference(model_unet, temp_masked_path, device)
    
    # Remove temporary file
    os.remove(temp_masked_path)

    # Convert prediction mask to numpy
    prediction_mask_np = tensor_to_numpy(prediction_mask)
    prediction_mask_np = (prediction_mask_np * 255).astype(np.uint8)

    # Apply morphological operations
    closed_mask = apply_morphological_operations(prediction_mask_np)

    # Create light gray color for background
    light_gray_color = np.array([110, 110, 110], dtype=np.uint8)
    
    # Convert original image to color for overlay
    color_original = cv2.cvtColor(original_image_normalized, cv2.COLOR_GRAY2RGB)
    
    overlay_image = _create_overlay(original_image_normalized, closed_mask)

    # Prepare image for ResNet classification
    transform = transforms.Compose([
        transforms.Lambda(to_3_channels),  # Convert grayscale to 3 channels
        transforms.ToPILImage(),           # Convert numpy image to PIL image
        transforms.Resize((224, 224)),     # Resize to fixed 224x224
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Convert result image to grayscale for ResNet
    gray_image = cv2.cvtColor(overlay_image, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    
    # Perform ResNet classification
    res_prediction = predict(model_resnet, gray_image, transform, device)
    print(res_prediction)
    
    # Convert images to base64
    # def convert_to_base64(image):
    #     # Convert the numpy array to a PIL Image
    #     pil_image = Image.fromarray(image)
        
    #     # Create a bytes buffer
    #     buffer = io.BytesIO()
        
    #     # Save the image to the buffer in PNG format
    #     pil_image.save(buffer, format="PNG")
        
    #     # Get the byte data from the buffer
    #     image_bytes = buffer.getvalue()
        
    #     # Encode the bytes to base64
    #     base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        
    #     return base64_encoded
    
    def convert_to_base64(lime_overlay):
        # Convert the numpy array to a PIL Image
        pil_image = Image.fromarray((lime_overlay * 255).astype(np.uint8))
        
        # Create a bytes buffer
        buffer = io.BytesIO()
        
        # Save the image to the buffer in PNG format
        pil_image.save(buffer, format="PNG")
        
        # Get the byte data from the buffer
        image_bytes = buffer.getvalue()
        
        # Encode the bytes to base64
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        
        return base64_encoded
    
    # def convert_tensor_to_base64(image_tensor):
    #     # Ensure the tensor is on the CPU and detach it from the computation graph
    #     image_tensor = image_tensor.cpu().detach()
    
    #     # Convert tensor to NumPy array
    #     image_array = image_tensor.numpy()

    #     # Check if the image has more than 3 channels and select one channel or handle it appropriately
    #     if image_array.ndim == 3 and image_array.shape[0] > 3:
    #         # For example, if you have a multi-class prediction with shape (num_classes, height, width)
    #         # You can take one channel or apply some logic to combine them.
    #         # Here we simply take the first channel as an example.
    #         image_array = image_array[0]  # Take the first channel

    #     # Squeeze if necessary to remove any singleton dimensions
    #     image_array = np.squeeze(image_array)

    #     # Ensure we have either a grayscale (H,W) or RGB (H,W,C) format
    #     if image_array.ndim == 2:  # Grayscale
    #         pil_image = Image.fromarray((image_array * 255).astype(np.uint8))
    #     elif image_array.ndim == 3 and image_array.shape[2] in [3, 4]:  # RGB or RGBA
    #         pil_image = Image.fromarray((image_array * 255).astype(np.uint8))
    #     else:
    #         raise ValueError("Unsupported image shape: {}".format(image_array.shape))

    #     # Create a bytes buffer
    #     buffer = io.BytesIO()

    #     # Save the image to the buffer in PNG format
    #     pil_image.save(buffer, format="PNG")

    #     # Get the byte data from the buffer
    #     image_bytes = buffer.getvalue()

    #     # Encode the bytes to base64
    #     base64_encoded = base64.b64encode(image_bytes).decode('utf-8')

    #     return base64_encoded
    
        # Base64 encode preprocessed image

    preprocessed_image_np = preprocessed_image.squeeze(0).cpu().numpy()
    preprocessed_image_np = ((preprocessed_image_np + 1) * 127.5).astype(np.uint8)
    _, preprocessed_image_buffer = cv2.imencode('.png', preprocessed_image_np)
    preprocessed_image_base64 = base64.b64encode(preprocessed_image_buffer).decode('utf-8')


    # Base64 encode overlay image

    _, overlay_image_buffer = cv2.imencode('.png', overlay_image)
    overlay_image_base64 = base64.b64encode(overlay_image_buffer).decode('utf-8')
    
    original_image_color = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
    
    return {
        "Predicted Class": res_prediction,
        "Preprocessed_image": preprocessed_image_base64,
        "SAR_mask": overlay_image_base64,
        "Original Image":convert_to_base64(original_image_color)
    }