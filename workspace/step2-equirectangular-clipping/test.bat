@REM 
@REM settings\settings0.toml
@REM settings\settings1.toml
@REM settings\settings2.toml
@REM のそれぞれに対して
@REM ファイル内の変数を変換して別名で保存
@REM debug_mode = false → debug_mode = true: _debug.toml
@REM filter = "none" → filter = "none": _none.toml
@REM filter = "none" → filter = "hexagonal_gaussian": _gaussian.toml
@REM filter = "none" → filter = "hexagonal_depth_gaussian": _depth_gaussian.toml
@REM 各ファイルの保存ディレクトリは settings\settings0_modifiers など
@REM もしディレクトリがなければ新規作成
set "settings=.\settings\settings0.toml .\settings\settings1.toml .\settings\settings2.toml"
set "modifiers=_debug.toml _none.toml _gaussian.toml _depth_gaussian.toml"

for %%s in (%settings%) do (
    for %%m in (%modifiers%) do (
        set "output=%%~ns%%~xm"
        set "output_dir=.\settings\%%~ns_modifiers"
        if not exist "!output_dir!" mkdir "!output_dir!"
        set "output=%%~ns%%~xm"
    )
)
