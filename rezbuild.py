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

    # variant 서브경로 구성 (imath-3.1.9 or imath-3.2.0)
    imath_ver = os.environ.get("REZ_IMATH_VERSION", "")
    variant_subpath = f"imath-{imath_ver}" if imath_ver else ""
    server_base = f"/core/Linux/APPZ/packages/ffmpeg/{version}"
    install_root = os.path.join(server_base, variant_subpath) if variant_subpath else server_base

    # 3) 의존성 경로 (REZ_*_ROOT 환경변수 활용)
    openssl_root = os.environ.get("REZ_OPENSSL_ROOT", "/core/Linux/APPZ/packages/openssl/3.0.16")
    libass_root  = os.environ.get("REZ_LIBASS_ROOT", "/core/Linux/APPZ/packages/libass/0.17.1")

    print(f"📦 Tarball:      {tar_path}")
    print(f"📂 Extract dir: {extract_dir}")
    print(f"📁 Install dir: {install_root}")
    print(f"🔗 OpenSSL:     {openssl_root}")
    print(f"🔗 libass:      {libass_root}")

    # 4) 클린업
    clean_build_dir(extract_dir)
    clean_build_dir(build_path)
    if "install" in targets:
        variant_idx = int(os.environ.get("REZ_BUILD_VARIANT_INDEX", "0"))
        # 첫 번째 variant 빌드 시 기존 전체 폴더 클린업 (구버전 flat 구조 제거)
        if variant_idx == 0:
            print(f"🧹 Removing entire install dir: {server_base}")
            shutil.rmtree(server_base, ignore_errors=True)
            os.makedirs(server_base, exist_ok=True)
        print(f"🧹 Removing variant install dir: {install_root}")
        shutil.rmtree(install_root, ignore_errors=True)

    # 5) 소스 압축 해제
    if not os.path.exists(tar_path):
        print(f"❌ tar.gz not found: {tar_path}")
        sys.exit(1)
    run_cmd(f"tar -xvf {tar_path}", cwd=os.path.dirname(tar_path))

    # 6) extra-cflags / extra-ldflags 통합 (마지막 값만 적용되므로 하나로 합침)
    extra_cflags = " ".join([
        f"-I{openssl_root}/include",
        f"-I{libass_root}/include",
    ])
    extra_ldflags = " ".join([
        f"-L{openssl_root}/lib",
        f"-L{libass_root}/lib",
    ])

    # 7) configure
    os.chdir(extract_dir)
    config_cmd = [
        "./configure",
        f"--prefix={install_root}",

        # 실행 파일
        "--enable-ffmpeg",
        "--enable-ffprobe",
        "--disable-ffplay",
        "--disable-doc",
        "--disable-debug",

        # 기본 라이브러리
        "--enable-avcodec",
        "--enable-avformat",
        "--enable-avutil",
        "--enable-swresample",
        "--enable-swscale",

        # 디코더
        "--enable-decoder=h264",
        "--enable-decoder=hevc",
        "--enable-decoder=vp8",
        "--enable-decoder=vp9",
        "--enable-decoder=av1",
        "--enable-decoder=aac",
        "--enable-decoder=mp3",
        "--enable-decoder=exr",
        "--enable-decoder=png",
        "--enable-decoder=tiff",
        "--enable-decoder=webp",
        "--enable-decoder=rawvideo",

        # 파서
        "--enable-parser=h264",
        "--enable-parser=hevc",
        "--enable-parser=vp8",
        "--enable-parser=vp9",
        "--enable-parser=av1",
        "--enable-parser=aac",

        # demuxer
        "--enable-demuxer=mov",
        "--enable-demuxer=matroska",
        "--enable-demuxer=ogg",
        "--enable-demuxer=image2",
        "--enable-demuxer=image2pipe",
        "--enable-demuxer=rawvideo",

        # muxer
        "--enable-muxer=mp4",
        "--enable-muxer=matroska",
        "--enable-muxer=webm",
        "--enable-muxer=image2",
        "--enable-muxer=image2pipe",

        # 인코더
        "--enable-encoder=libx264",
        "--enable-encoder=libx265",
        "--enable-encoder=libaom-av1",
        "--enable-encoder=libvpx-vp9",
        "--enable-encoder=exr",
        "--enable-encoder=prores",
        "--enable-encoder=prores_ks",
        "--enable-encoder=prores_aw",

        # 프로토콜
        "--enable-protocol=file",
        "--enable-protocol=pipe",
        "--enable-protocol=https",
        "--enable-protocol=http",
        "--enable-protocol=tls",
        "--enable-protocol=tcp",
        "--enable-protocol=udp",

        # 비트스트림 필터
        "--enable-bsf=aac_adtstoasc",
        "--enable-bsf=hevc_mp4toannexb",
        "--enable-bsf=h264_mp4toannexb",

        # 외부 라이브러리
        "--enable-openssl",
        "--enable-libx264",
        "--enable-libx265",
        "--enable-libvpx",
        "--enable-libfdk-aac",
        "--enable-libopus",
        "--enable-libvorbis",
        "--enable-libmp3lame",
        "--enable-libaom",
        "--enable-libdav1d",
        "--enable-libvmaf",
        "--enable-libxvid",
        "--enable-libdrm",
        "--enable-libfreetype",
        "--enable-libharfbuzz",
        "--enable-libass",
        "--enable-libzimg",
        "--enable-libplacebo",

        # 필터
        "--enable-filter=drawtext",
        "--enable-filter=ass",
        "--enable-filter=subtitles",
        "--enable-filter=zscale",
        "--enable-filter=tonemap",
        "--enable-filter=format",
        "--enable-filter=scale",
        "--enable-filter=libplacebo",
        "--enable-filter=hwupload",
        "--enable-filter=hwdownload",

        # HW 가속
        "--enable-vaapi",
        "--enable-libxcb",
        "--enable-libxcb-shm",
        "--enable-libxcb-xfixes",
        "--enable-libxcb-shape",
        "--enable-hwaccel=hevc_vaapi",
        "--enable-hwaccel=vp9_vaapi",
        "--enable-hwaccel=av1_vaapi",

        # 라이센스
        "--enable-gpl",
        "--enable-nonfree",

        # 빌드 옵션
        "--enable-pic",
        "--enable-shared",
        "--disable-static",
        "--disable-vulkan",

        # 통합 플래그 (각각 한 번만 지정)
        f"--extra-cflags={extra_cflags}",
        f"--extra-ldflags={extra_ldflags}",

        "--logfile=config.log",
    ]
    try:
        subprocess.run(config_cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ configure failed. config.log 확인하세요.")
        sys.exit(1)

    # 8) make & install
    try:
        run_cmd("make -j$(nproc)")
    except subprocess.CalledProcessError:
        print("❌ make failed.")
        sys.exit(1)

    if "install" in targets:
        try:
            run_cmd("make install")
            copy_package_py(source_path, server_base)
            print(f"✅ Installed to {install_root}")
        except subprocess.CalledProcessError:
            print("❌ install failed.")
            sys.exit(1)

    # variant.json 생성 (rez 패키지 등록에 필요)
    variant_json = os.path.join(build_path, "variant.json")
    with open(variant_json, "w") as f:
        f.write("{}\n")

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



