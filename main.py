import asyncio
import os
import httpx
from pytube import YouTube
from tqdm import tqdm
import validators

async def download_video(url, download_dir):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    total_size = stream.filesize

    async with httpx.AsyncClient() as client:
        async with client.stream('GET', stream.url) as response:

            if response.status_code == 200:
                filename = os.path.join(download_dir, stream.default_filename).replace(" ", "_")
                os.makedirs(download_dir, exist_ok=True)
                ind = url.find("?v=")
                name = f"{url[ind + 3:]} | {stream.default_filename[:10]}..."

                tqdm_params = {
                    'desc': f"Downloading {name}",
                    'total': total_size,
                    'unit': 'B',
                    'unit_scale': True,
                    'unit_divisor': 1024,
                    'leave': True,
                    'dynamic_ncols': True,
                    'miniters': 1,  # Минимальное количество итераций для обновления прогресса
                    'smoothing': 0.01  # Сглаживание для прогресса
                }

                with open(filename, 'wb') as f:
                    with tqdm(**tqdm_params) as pbar:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                            pbar.update(len(chunk))
                            await asyncio.sleep(0)
            else:
                ind = url.find("?v=")
                print(f"Error!\turl: {url[ind + 3:]}\tstatus code: {response.status_code}")


async def main():
    download_dir = os.path.join(os.getcwd(), 'download')
    urls = []
    while True:
        url = input("Enter YouTube URL (or type 'done' to finish): ")
        if url.lower() in ['done', '-', '.', '']:
            break
        if validators.url(url):
            urls.append(url)
        else:
            print("Invalid URL. Please enter a valid YouTube URL.")

    tasks = [download_video(url, download_dir) for url in urls]
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    asyncio.run(main())
