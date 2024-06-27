# フォルダ構造
jim
- workflow: プログラムなど全部入っている
    - step1-panorama-rendering: Blenderのレンダリング結果を入れるための場所
        - （想定）output_color/
        - （想定）output_depth/
        - test_generate_check_videos.bat: colorの画像を動画化するバッチファイル（デプスはexr未対応なので）
    - step2-equirectangular-clipping
        - code/ : 全てのコードが含まれる
            - hexagonal_filter.py : 六角形化、ぼかし、等実行
            - sphere_to_plane.py : 球面に張り付けてクリッピング
            - viewer.py : 上記二つを呼び出す
        - run.bat : viewerを起動
        - 
# Setup
```
setup.bat
```

# Usage
```
run.bat
```
