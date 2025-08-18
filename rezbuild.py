# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import importlib.util

def run_cmd(cmd, cwd=None):
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, cwd=cwd, shell=True, check=True)

def clean_build_dir(build_path):
    if os.path.exists(build_path):
        print(f"🧹 Cleaning build directory (excluding build.rxt): {build_path}")
        for item in os.listdir(build_path):
            item_path = os.path.join(build_path, item)
            # build.rxt 마커는 보존
            if os.path.isfile(item_path) and item.endswith(".rxt"):
                print(f"🔒 Preserving {item}")
                continue
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        os.makedirs(build_path, exist_ok=True)

def copy_package_py(source_path, install_path):
    src_pkg = os.path.join(source_path, "package.py")
    dst_pkg = os.path.join(install_path, "package.py")
    if os.path.exists(src_pkg):
        print(f"📄 Copying package.py → {dst_pkg}")
        shutil.copy(src_pkg, dst_pkg)
    else:
        print("⚠️ package.py not found in source_path!")

def get_package_version():
    pkg_path = os.path.join(os.path.dirname(__file__), "package.py")
    spec = importlib.util.spec_from_file_location("package", pkg_path)
    pkg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pkg)
    return getattr(pkg, "version", "unknown")

def build(source_path, build_path, install_path, targets):
    # 1) 버전 결정
    version = os.environ.get("REZ_BUILD_PROJECT_VERSION") or get_package_version()

    # 2) 경로 설정
    tar_path     = os.path.join(source_path, "source", f"ffmpeg-{version}.tar.gz")
    extract_dir  = os.path.join(source_path, "source", f"ffmpeg-{version}")
    install_root = f"/core/Linux/APPZ/packages/ffmpeg/{version}"

    print(f"📦 Tarball:      {tar_path}")
    print(f"📂 Extract dir: {extract_dir}")
    print(f"📁 Install dir: {install_root}")

    # 3) 클린업
    clean_build_dir(extract_dir)
    clean_build_dir(build_path)
    if "install" in targets:
        print(f"🧹 Removing install dir: {install_root}")
        shutil.rmtree(install_root, ignore_errors=True)

    # 4) 소스 압축 해제
    if not os.path.exists(tar_path):
        print(f"❌ tar.gz not found: {tar_path}")
        sys.exit(1)
    run_cmd(f"tar -xvf {tar_path}", cwd=os.path.dirname(tar_path))

    # 5) configure
    os.chdir(extract_dir)
    config_cmd = [
                "./configure",
        f"--prefix={install_root}",
        "--enable-ffmpeg",  # ffmpeg 실행 파일 생성
        "--enable-ffprobe",  # ffprobe 실행 파일 생성
        "--disable-ffplay",  # ffplay 불필요시 비활성화
        "--disable-doc",
        "--disable-debug",
        "--disable-everything",  # 필요한 것만 enable

        # 기본 라이브러리
        "--enable-avcodec",
        "--enable-avformat",
        "--enable-avutil",
        "--enable-swresample",
        "--enable-swscale",

        # 디코더
        "--enable-decoder=h264",
        "--enable-decoder=aac",
        "--enable-decoder=vp8",
        "--enable-decoder=mp3",

        # demuxer
        "--enable-demuxer=mov",
        "--enable-demuxer=matroska",  # webm 포함
        "--enable-demuxer=ogg",

        # parser
        "--enable-parser=h264",
        "--enable-parser=aac",
        "--enable-parser=vp8",

        # protocol & bsf
        "--enable-protocol=file",
        "--enable-bsf=aac_adtstoasc",

        "--enable-protocol=https",
        "--enable-protocol=http",
        "--enable-protocol=tls",
        "--enable-protocol=tcp",
        "--enable-protocol=udp",

        # 외부 라이브러리
        "--enable-libopus",
        "--enable-libvorbis",
        "--enable-libmp3lame",

        "--enable-openssl",
        f"--extra-cflags=-I/core/Linux/APPZ/packages/openssl/3.0.16/include",
        f"--extra-ldflags=-L/core/Linux/APPZ/packages/openssl/3.0.16/lib",

        # 기타
        "--enable-pic",
        "--enable-shared",
        "--disable-static",

        # 추가
        "--enable-libx264",
        "--enable-libx265",
        "--enable-libvpx",
        "--enable-libfdk-aac",
        "--enable-libvorbis",
        "--enable-libmp3lame",
        "--enable-libdrm",
        "--enable-vaapi",
        "--enable-libxcb",
        "--enable-libxcb-shm",
        "--enable-libxcb-xfixes",
        "--enable-libxcb-shape",
        "--enable-libaom",
        "--enable-libdav1d",
        "--enable-libvmaf",
        "--enable-libxvid",
        "--enable-gpl",
        "--enable-nonfree",

        "--logfile=config.log"
    ]
    try:
        subprocess.run(config_cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ configure failed. config.log 확인하세요.")
        sys.exit(1)

    # 6) make & install
    try:
        run_cmd("make -j$(nproc)")
    except subprocess.CalledProcessError:
        print("❌ make failed.")
        sys.exit(1)

    if "install" in targets:
        try:
            run_cmd("make install")
            copy_package_py(source_path, install_root)
            print(f"✅ Installed to {install_root}")
        except subprocess.CalledProcessError:
            print("❌ install failed.")
            sys.exit(1)

    print("✅ FFmpeg build completed.")

if __name__ == "__main__":
    build(
        source_path  = os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path   = os.environ["REZ_BUILD_PATH"],
        install_path = os.environ["REZ_BUILD_INSTALL_PATH"],
        targets      = sys.argv[1:]
    )


"""
빌드후 확인 사항
./bin/ffmpeg -protocols | grep https     # https 사용 가능한지
ldd ./bin/ffmpeg | grep ssl
ldd ./lib/libavformat.so | grep ssl  # openssl 동적 링크 확인
ldd ./lib/libavutil.so.57 | grep ssl
./ffmpeg -protocols | grep https
./ffmpeg -buildconf | grep openssl
"""



