import torch
import torchvision.transforms as transforms
import torchvision.models as models
import cv2

class CourtLineDetector:
    def __init__(self,model_path):
        self.model = models.resnet50(pretrained=False)
        self.model.fc = torch.nn.Linear(self.model.fc.in_features,14*2)
        self.model.load_state_dict(torch.load(model_path,map_location='cpu'))

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self,image):
        img = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        img_tensor = self.transform(img).unsqueeze(0)

        with torch.no_grad():
            outputs = self.model(img_tensor)

        keypoints = outputs.squeeze().cpu().numpy()
        original_h,original_w = img.shape[:2]

        keypoints[::2] *= original_w/224.0
        keypoints[1::2] *= original_h/24.0

        return keypoints
    
    def draw_keypoints(self,image,keypoints):
        for i in range(0,len(keypoints),2):
            x = int(keypoints[i])
            y = int(keypoints[i+1])

            cv2.putText(image,str(i//2),(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
            cv2.circle(image,(x,y),5,(0,0,255),-1)
        return image
    
    def draw_keypoints_on_videoframes(self,video_frames,keypoints):
        output_video_frames = []
        for frame in video_frames:
            output_frame = self.draw_keypoints(frame,keypoints)
            output_video_frames.append(output_frame)
        return output_video_frames
