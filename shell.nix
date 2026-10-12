# The release archive and unpacked SHA-256 are pinned, not the user's channels.
{ pkgs ? import (builtins.fetchTarball {
    url = "https://releases.nixos.org/nixos/26.05/nixos-26.05.8409.f4f698677b11/nixexprs.tar.xz";
    sha256 = "0xay5mb4ajycx774f3x7ckn16xngxwh4l7s9iy11jrdwjgvvzfxm";
  }) {} }:
pkgs.mkShell {
  packages = [ pkgs.python3 pkgs.gcc pkgs.git ];
  shellHook = ''
    export PYTHONNOUSERSITE=1
  '';
}
