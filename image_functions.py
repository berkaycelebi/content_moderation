
import torchvision.transforms as transforms
import torch
import model_loader as ml

# To detect violence
def isviolence(img) -> bool:
    """Checks for violence in the given image

    Args:
      img: A image object to be checked

    Returns:
      Boolean

    Raises:
      IOError – If the file cannot be found, or the image
                cannot be opened and identified

    """
    class_names = ["safe", "unsafe"]
    standard_normalization = transforms.Normalize(
        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    )
    try:

        def load_input_image(img):
            image = img.convert("RGB")
            prediction_transform = transforms.Compose(
                [
                    transforms.Resize(size=(224, 224)),
                    transforms.ToTensor(),
                    standard_normalization,
                ]
            )

            image = prediction_transform(image)[:3, :, :].unsqueeze(0)
            return image

        def predict_image(model, class_names, img):
            # load the image and return the predicted breed
            img = load_input_image(img)
            model = model.cpu()
            model.eval()
            idx = torch.argmax(model(img))
            return class_names[idx]

        def run_app(img):

            prediction = predict_image(ml.violence_model, class_names, img)
            return prediction

        p = run_app(img)
        return 0 if p == "safe" else 1
    except IOError:
        return 1

# -----------------------------------------------#

# To detect nudity
def isnudityImage(img) -> bool:
    response = ml.nudeClassifier.classify(img)
    unsafe = response[img]['unsafe']
    return True if unsafe > 0.65 else False

def isnudityVideo(path) -> bool:
    response = ml.nudeClassifier.classify_video(path, batch_size=4)

    for pred in response['preds'].values():
        if(pred['unsafe'] > 0.9):
            return True
    
    return False