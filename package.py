# -*- coding: utf-8 -*-
name        = "ffmpeg"
version     = "6.1.1"
authors     = ["M83"]
description = "FFmpeg build for QtMultimedia & QtWebEngine compatibility"

build_requires = [
    "gcc-11.5.0",
    "cmake-3.26.5",
    "python-3.13.2",   # VFX 플랫폼 표준 Python
    "make-4.4",
]

requires = [
    "openssl-3.0.16",   # VFX 플랫폼 통일 OpenSSL
    "libvpx-1.13.1",
    "libvmaf-2.3.1",
    "aom-3.8.1",
    "libdrm-2.4.120",
    "libfdk_aac-2.0.2",
    "xvidcore-1.3.7",
    "dav1d-1.2.1",
    "x264-20240210",
    "x265-3.5",
    "libopus-1.4",
    "libvorbis-1.3.7",
    "lame-3.100",
]

tools=[
'ffmpeg',
'ffprobe'
]

variants = []

build_command = "python {root}/rezbuild.py {install}"

def commands():
    # 실행 바이너리
    env.PATH.append("{root}/bin")
    # 런타임 라이브러리 로딩 및 RPATH
    env.LD_LIBRARY_PATH.append("{root}/lib")
    env.LD_LIBRARY_PATH.append("/core/Linux/APPZ/packages/libvpx/1.13.1/lib")
    # pkg-config 검색 경로 (lib 및 lib64)
    env.PKG_CONFIG_PATH.append("{root}/lib/pkgconfig")
    # FFmpeg root
    env.FFMPEG_ROOT = "{root}"

