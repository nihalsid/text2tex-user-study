from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from pathlib import Path
import random
from django.views.decorators.csrf import csrf_exempt
import datetime


def index(request):
    return render(request, 'index.html')


def index_text2room(request):
    return render(request, 'index_text2room.html')


def get_form(request):
    data = {
        "title": "Text2Tex User Study",
        "description": "Each question shows objects textured by two different approaches. Each option image shows the textured object rendered from 8 different viewpoints. Select the one that looks more realistic.",
        "elements": []
    }
    num_samples = 15
    baseline_names = ["clip_mesh", "latent_paint", "text2mesh"]
    render_paths = random.sample(list(Path("static/renders").iterdir()), num_samples)
    for i in range(num_samples):
        render_path = render_paths[i]
        category = " ".join(render_path.stem.split("_")[:-1])
        element = {
            "type": "imagepicker",
            "name": "Which of the textured objects best represents \"" + category + "\"?",
            "imageHeight": "518px",
            "imageWidth": "1034px",
            "isRequired": "true",
            "choices": [
            ]
        }
        baseline = baseline_names[i % len(baseline_names)]
        element["choices"].append({
            "value": f"{baseline}/ours",
            "imageLink": f"/static/renders/{render_path.stem}/ours.jpg",
        })
        element["choices"].append({
            "value": f"{baseline}/{baseline}",
            "imageLink": f"/static/renders/{render_path.stem}/{baseline}.jpg",
        })
        random.shuffle(element["choices"])
        data["elements"].append(element)
    random.shuffle(data["elements"])
    data["elements"] = [{
      "type": "text",
      "name": "name",
      "title": "Enter your name:",
      "isRequired": "true",
    }] + data["elements"]
    return JsonResponse(data)


def get_form_text2room(request):
    data = {
        "title": "Text2Room User Study",
        "description": "Instructions for User",
        "pages": [],
        "showQuestionNumbers": "off"
    }

    num_samples = 2

    for i in range(num_samples):
        random_sample = random.choice(list(Path("static/renders").iterdir()))
        data["pages"].append({
                "name": f"item_{i}",
                "elements": [
                    {
                        "type": "image",
                        "name": f"image_sample_{i}",
                        "imageLink": f"/static/renders/{random_sample.stem}/ours.jpg"
                    },
                    {
                        "type": "rating",
                        "name": f"item_{i}_question_0",
                        "title": "On a scale of zero to ten, how likely are you to recommend our product to a friend or colleague?",
                        "isRequired": "true",
                        "rateMin": 1,
                        "rateMax": 5,
                        "minRateDescription": "(Most unlikely)",
                        "maxRateDescription": "(Most likely)"
                    },
                    {
                        "type": "rating",
                        "name": f"item_{i}_question_1",
                        "title": "On a scale of zero to ten, how likely are you to recommend our product to a friend or colleague?",
                        "isRequired": "true",
                        "rateMin": 1,
                        "rateMax": 5,
                        "minRateDescription": "(Most unlikely)",
                        "maxRateDescription": "(Most likely)"
                    }
                ]
        })

    data["pages"][0]["elements"] = [{
        "type": "text",
        "name": "name",
        "title": "Enter your name:",
        "isRequired": "true",
    }] + data["pages"][0]["elements"]

    return JsonResponse(data)


def generate_name(name):
    study_name = f"{datetime.datetime.now().strftime('%m%d%H%M')}_{name}.csv"
    return study_name


@csrf_exempt
def submit(request):
    username = request.GET['name']
    items = []
    for k in request.GET:
        if k != "name":
            items.append(",".join([k, request.GET[k]]))
    csv = "\n".join(items)
    Path("results", generate_name(username)).write_text(csv)
    return HttpResponse(status=200)


@csrf_exempt
def submit_text2room(request):
    username = request.GET['name']
    items = []
    for k in request.GET:
        if k != "name":
            items.append(",".join([k, request.GET[k]]))
    csv = "\n".join(items)
    Path("results", "text2room_" + generate_name(username)).write_text(csv)
    return HttpResponse(status=200)
