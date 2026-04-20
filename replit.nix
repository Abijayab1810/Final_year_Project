{ pkgs }: {
    deps = [
        pkgs.python311
        pkgs.python311Packages.pip
        pkgs.virtualenv
        pkgs.libsm
        pkgs.libxext
        pkgs.libxrender
    ];
}
