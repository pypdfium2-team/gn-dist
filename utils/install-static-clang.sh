#!/bin/bash
# SPDX-FileCopyrightText: 2025 Matthieu Darbois
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: From scikit-build/ninja-python-distributions. License assumed from project license.

# Stop at any error, show all commands
set -exuo pipefail

TOOLCHAIN_PATH=/opt/clang

# Download static-clang
DEFAULT_ARCH="$(uname -m)"
if [ "${STATIC_CLANG_ARCH:-}" == "" ]; then
	STATIC_CLANG_ARCH="${RUNNER_ARCH:-${DEFAULT_ARCH}}"
fi
case "${STATIC_CLANG_ARCH}" in
	ARM64|aarch64|arm64|arm64/*) GO_ARCH=arm64;;
	ARM|armv7l|armv8l|arm|arm/v7) GO_ARCH=arm;;  # assume arm/v7 for arm
	X64|x86_64|amd64|amd64/*) GO_ARCH=amd64;;
	X86|i686|386) GO_ARCH=386;;
	loongarch64) GO_ARCH=loong64;;
	ppc64le) GO_ARCH=ppc64le;;
	riscv64) GO_ARCH=riscv64;;
	s390x) GO_ARCH=s390x;;
	*) echo "No static-clang toolchain for ${CLANG_ARCH}">2; exit 1;;
esac
STATIC_CLANG_VERSION=22.1.7.0
STATIC_CLANG_FILENAME="static-clang-linux-${GO_ARCH}.tar.xz"
STATIC_CLANG_URL="https://github.com/mayeut/static-clang-images/releases/download/v${STATIC_CLANG_VERSION}/${STATIC_CLANG_FILENAME}"
pushd /tmp
cat<<'EOF' | grep "${STATIC_CLANG_FILENAME}" > "${STATIC_CLANG_FILENAME}.sha256"
2cf4ea4200229311b23856fac7fedd53ddd4cd096b65b8be968019686edce769  static-clang-linux-386.tar.xz
85a5f0fe9c7dcac29a30fe924356dcd2b3dc5d539023895f2b6922e7c416e8a9  static-clang-linux-amd64.tar.xz
0021fd7c4b7411d8a8db6c7042dfa497788222c97c1d1f9ae7b2764c29079bf9  static-clang-linux-arm.tar.xz
793aaac0436ab4f3b2594f35ab4078277db627c940d5097a72ea291a0fd3802e  static-clang-linux-arm64.tar.xz
1b74895af70afcc81d1d63453ca20d4f49e87897f8f4c106ddaea4f3020eb6c4  static-clang-linux-loong64.tar.xz
73db8f9d2aaaf7c4e24337bea2a9ddd8a08413ec9bc0d41c54d6992d1041d202  static-clang-linux-ppc64le.tar.xz
b82aa55106d528ba0b9aa9edc8b05e36673c0717f5a33d73f4af8062dc86f767  static-clang-linux-riscv64.tar.xz
f96b997498d42e152f7c9a822989bf540ed58edc5dfe9c7643031ab71ffa0643  static-clang-linux-s390x.tar.xz
EOF
curl -fsSLO "${STATIC_CLANG_URL}"
sha256sum -c "${STATIC_CLANG_FILENAME}.sha256"
tar -C /opt -xf "${STATIC_CLANG_FILENAME}"
popd

# configure target triple
case "${AUDITWHEEL_POLICY}-${AUDITWHEEL_ARCH}" in
	manylinux*-armv7l) TARGET_TRIPLE=armv7-unknown-linux-gnueabihf;;
	musllinux*-armv7l) TARGET_TRIPLE=armv7-alpine-linux-musleabihf;;
	manylinux*-ppc64le) TARGET_TRIPLE=powerpc64le-unknown-linux-gnu;;
	musllinux*-ppc64le) TARGET_TRIPLE=powerpc64le-alpine-linux-musl;;
	manylinux*-*) TARGET_TRIPLE=${AUDITWHEEL_ARCH}-unknown-linux-gnu;;
	musllinux*-*) TARGET_TRIPLE=${AUDITWHEEL_ARCH}-alpine-linux-musl;;
esac
case "${AUDITWHEEL_POLICY}-${AUDITWHEEL_ARCH}" in
	*-riscv64) M_ARCH="-march=rv64gc";;
	*-x86_64) M_ARCH="-march=x86-64";;
	*-armv7l) M_ARCH="-march=armv7a";;
	manylinux*-i686) M_ARCH="-march=k8 -mtune=generic";;  # same as gcc manylinux2014 / manylinux_2_28
	musllinux*-i686) M_ARCH="-march=pentium-m -mtune=generic";;  # same as gcc musllinux_1_2
esac
GCC_TRIPLE=$(gcc -dumpmachine)

cat<<EOF >"${TOOLCHAIN_PATH}/bin/${AUDITWHEEL_PLAT}.cfg"
	-target ${TARGET_TRIPLE}
	${M_ARCH:-}
	--gcc-toolchain=${DEVTOOLSET_ROOTPATH:-}/usr
	--gcc-triple=${GCC_TRIPLE}
EOF

cat<<EOF >"${TOOLCHAIN_PATH}/bin/clang.cfg"
	@${AUDITWHEEL_PLAT}.cfg
EOF

cat<<EOF >"${TOOLCHAIN_PATH}/bin/clang++.cfg"
	@${AUDITWHEEL_PLAT}.cfg
EOF

cat<<EOF >"${TOOLCHAIN_PATH}/bin/clang-cpp.cfg"
	@${AUDITWHEEL_PLAT}.cfg
EOF

# override entrypoint to add the toolchain to PATH
mv /usr/local/bin/manylinux-entrypoint /usr/local/bin/manylinux-entrypoint-org
cat<<EOF >/usr/local/bin/manylinux-entrypoint
#!/bin/bash

set -eu

export PATH="${TOOLCHAIN_PATH}/bin:\${PATH}"
exec /usr/local/bin/manylinux-entrypoint-org "\$@"
EOF

chmod +x /usr/local/bin/manylinux-entrypoint
