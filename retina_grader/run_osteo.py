#Runs the Osteomyelitis in batch

import argparse
import torch.nn as nn
import torch

import pydicom
import numpy as np

from PIL import Image
import json
import os
class VGG_net(nn.Module):
    
    def __init__(self, in_channels=3, num_classes=1, LAYERS=[64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M']): #Defaults to VGG16. Change layers to adjust.
        super(VGG_net, self).__init__()
        self.in_channels = in_channels
        self.avgpool = nn.AdaptiveAvgPool2d((7, 7))
        self.conv_layers = self.create_conv_layers(LAYERS)
        self.fcs = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(512*7*7, 4096),
            nn.ReLU(True),
            nn.Dropout(p=0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Linear(4096, num_classes))
    
    def create_conv_layers(self, architecture):
        layers = []
        in_channels = self.in_channels
        for x in architecture:
            if type(x) == int:
                out_channels = x
                layers += [ nn.Conv2d(in_channels=in_channels, out_channels=out_channels,
                                      kernel_size=(3,3), stride=(1,1), padding=(1,1)),
                           nn.BatchNorm2d(x),
                           nn.ReLU() ]
                in_channels = x
            elif x == 'M':
                layers += [nn.MaxPool2d(kernel_size=(2,2), stride=(2,2))]
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.conv_layers(x)
        x = self.avgpool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fcs(x)
        return x
    


# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, help="Path to the source file or directory")
parser.add_argument("--output_folder", required=True, help="Path to the output folder")
args = parser.parse_args()

# Print the arguments
print(f"Source: {args.source}")
print(f"Output folder: {args.output_folder}")



# im  =  pydicom.dcmread(r'/home/radiology/Downloads/C7895578-1-0-f43a82ac-4393f374-946b775e-fbf5e5b2-90334078.dcm')
# im  = im.pixel_array
# im = (im - np.min(im)) / (np.max(im) - np.min(im))
dfo_vgg16_weights_path = r'/Users/vig00a/code/sianno-xray-github/df_osteo_detection_program/dfo_vgg16_weights.pt'
if os.getenv('dfo_vgg16_weights_path'):
    dfo_vgg16_weights_path = os.environ.get('dfo_vgg16_weights_path')
model = VGG_net().to(device="cpu")
x = torch.load(dfo_vgg16_weights_path
               , map_location=torch.device('cpu')
               )
print("loaded the osteo model")
model.load_state_dict(x)
model.train(False)

m=nn.Sigmoid()
results = []

for filename in os.listdir(args.source):
    print(f"for file name {filename}")
    if filename.lower().endswith(".jpg") or filename.lower().endswith(".png"):
        image_path = os.path.join(args.source, filename)
        with open(image_path, 'rb') as f:
            image = Image.open(f)
            image_resized = image.resize((224, 224))

            image_array = np.asarray(image_resized)
            image_array = (image_array - np.min(image_array)) / (np.max(image_array) - np.min(image_array))
            image_array = np.stack((image_array,)*3, axis=0)

            # image = torch.from_numpy(image).to(device='cuda', dtype=torch.float32)
            image_np = torch.from_numpy(image_array).to(device='cpu',dtype=torch.float32)
            print(f"shape of image_np {image_np.shape} ")

            image_np = torch.unsqueeze(image_np, 0)
            print(f"shape of image_np after squeeze {image_np.shape} ")

            print("about to predict")
            output = model(image_np)
            print("predicted")

            output = m(output)
            #output = [int(value > 0.5) for value in output]
            print({'prediction': output.detach().item()})
            results.append({"rect_id" : filename.split(".")[0],
                            "osteomyelitis_present_score" : float(output.detach().item()) })

#write the results to the results.txt file
            
with open(os.path.join(args.output_folder,"results.txt"), "w") as f:
    f.write(json.dumps(results))



