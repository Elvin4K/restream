import streamlink
import sys
import os 
import json
import traceback

def info_to_text(stream_info, url):
    # Senin istediğin sabit ve zenginleştirilmiş format
    text = '#EXT-X-STREAM-INF:'
    text += 'BANDWIDTH=8000000,'
    text += 'AVERAGE-BANDWIDTH=6500000,'
    
    if stream_info.resolution:
        text += f'RESOLUTION={stream_info.resolution.width}x{stream_info.resolution.height},'
    
    text += 'FRAME-RATE=25.000,'
    text += 'CODECS="avc1.640029,mp4a.40.2",'
    text += 'NAME="1080p Premium"' # Buraya istediğin ismi yazdım

    text = text + "\n" + url + "\n"
    return text

def main():
    print("=== Starting stream processing (Premium Format) ===")
    
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

    folder_name = config["output"]["folder"]
    best_folder_name = config["output"]["bestFolder"]
    root_folder = os.path.join(os.getcwd(), folder_name)
    best_folder = os.path.join(root_folder, best_folder_name)
    
    os.makedirs(best_folder, exist_ok=True)

    channels = config["channels"]
    success_count = 0
    fail_count = 0

    for idx, channel in enumerate(channels, 1):
        slug = channel.get("slug", "unknown")
        url = channel.get("url", "")
        
        print(f"[{idx}/{len(channels)}] Processing: {slug}")
        
        try:
            streams = streamlink.streams(url)
            
            if not streams or 'best' not in streams:
                fail_count += 1
                continue
            
            # En iyi yayının bilgilerini alıyoruz
            best_stream = streams['best']
            playlist_url = best_stream.url # Gerçek m3u8 linki
            
            # İstediğin başlık yapısını oluşturuyoruz
            best_text = "#EXTM3U\n"
            best_text += "#EXT-X-VERSION:3\n"
            best_text += "#EXT-X-INDEPENDENT-SEGMENTS\n"
            
            # Stream bilgilerini ekliyoruz
            best_text += info_to_text(best_stream, playlist_url)

            best_file_path = os.path.join(best_folder, slug + ".m3u8")

            with open(best_file_path, "w+") as best_file:
                best_file.write(best_text)
            
            print(f"  ✅ Premium Format Created")
            success_count += 1
                
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            fail_count += 1
    
    print(f"\n✅ Finished! Successful: {success_count}")

if __name__=="__main__": 
    main()
