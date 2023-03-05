from pathlib import Path
from PIL import Image
import numpy as np
from torchvision.transforms import ToTensor
from torchvision.utils import save_image
import torch
from tqdm import tqdm

RENDER_RESOLUTION = 512
FINAL_RESOLUTION = 256

views = [
    "2.00_015_000", "2.00_015_045", "2.00_015_135", "2.00_015_225",
    "2.00_045_030", "2.00_045_165", "2.00_045_255", "2.00_045_300",
]


def get_render_text2mesh(sample_path):
    render_paths = [sample_path / "render" / f"{x}.png" for x in views]
    return render_paths


def get_render_latentpaint(sample_path):
    render_paths = [sample_path / "mesh" / "render" / f"{x}.png" for x in views]
    return render_paths


def get_render_clipmesh(sample_path):
    render_paths = [sample_path / "meshes" / "mesh_0" / "render" / f"{x}.png" for x in views]
    return render_paths


def get_render_ours(sample_path):
    render_paths = [sample_path / f"{x}.png" for x in views]
    return render_paths


def crop_to_extents_and_get_arr(img, pad=True, white_bg=True):
    mask = np.array(img)[:, :, -1] > 0
    inds = np.where(mask)
    bounds_y = [inds[0].min(), inds[0].max()]
    bounds_x = [inds[1].min(), inds[1].max()]
    bounds_range_y = bounds_y[1] - bounds_y[0]
    bounds_range_x = bounds_x[1] - bounds_x[0]
    if bounds_range_y > bounds_range_x:
        top = bounds_y[0]
        bottom = bounds_y[1]
        left = (RENDER_RESOLUTION - bounds_range_y) / 2
        right = (RENDER_RESOLUTION + bounds_range_y) / 2
    else:
        left = bounds_x[0]
        right = bounds_x[1]
        top = (RENDER_RESOLUTION - bounds_range_x) / 2
        bottom = (RENDER_RESOLUTION + bounds_range_x) / 2
    if white_bg:
        np_img = np.array(img)
        mask = np_img[:, :, -1] < 1
        np_img[mask, :] = 255
        img = Image.fromarray(np_img[:, :, :-1])
    img = img.crop((left, top, right, bottom))
    img = img.resize((RENDER_RESOLUTION, RENDER_RESOLUTION), resample=Image.LANCZOS)
    if pad:
        result = Image.new(img.mode, (int(RENDER_RESOLUTION * 1.2), int(RENDER_RESOLUTION * 1.2)), (255, 255, 255))
        result.paste(img, (int(RENDER_RESOLUTION * 0.1), int(RENDER_RESOLUTION * 0.1)))
        img = result
    img = img.resize((FINAL_RESOLUTION, FINAL_RESOLUTION), resample=Image.LANCZOS)
    return ToTensor()(np.array(img))


def create_static():
    output_dir = Path("react/public/renders")
    output_dir.mkdir(exist_ok=True)
    ours = Path("/cluster/valinor/dchen/Text2Tex/evaluation_renders/42-p36-h20-1.0-0.3-update/19")
    text2mesh = Path("/rhome/ysiddiqui/text2mesh/results")
    clip_mesh = Path("/rhome/ysiddiqui/CLIP-Mesh/output")
    latent_paint = Path("/rhome/ysiddiqui/latent-nerf/experiments")

    all_methods = {
        "ours": (ours, get_render_ours),
        "text2mesh": (text2mesh, get_render_text2mesh),
        "clip_mesh": (clip_mesh, get_render_clipmesh),
        "latent_paint": (latent_paint, get_render_latentpaint)
    }

    all_samples = [x.name for x in list(ours.iterdir())]

    for method in all_methods:
        path, accessor = all_methods[method]
        for sample in tqdm(all_samples, desc=method):
            (output_dir / sample).mkdir(exist_ok=True)
            render_paths = accessor(path / sample)
            combined_arrs = []
            try:
                for p in render_paths:
                    combined_arrs.append(crop_to_extents_and_get_arr(Image.open(p)).unsqueeze(0))
                save_image(torch.cat(combined_arrs, 0), output_dir / sample / f"{method}.jpg", value_range=(0, 1), nrow=4, normalize=False)
            except:
                print(f"Shape Exception for {method} on {sample}")


if __name__ == "__main__":
    create_static()
