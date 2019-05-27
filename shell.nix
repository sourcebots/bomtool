{ pkgs ? import <nixpkgs> {} }:

# Note that as of 2019-01-21, pipenv is currently broken in the NixOS 18.09 release.
# https://github.com/NixOS/nixpkgs/issues/51970
# To work around, invoke with:
# nix-shell -E 'import ./shell.nix { pkgs = import (fetchTarball https://nixos.org/channels/nixpkgs-unstable/nixexprs.tar.xz) {}; }'

pkgs.stdenv.mkDerivation {
  name = "sb-bomtool-env";
  buildInputs = with pkgs; [
    python36
    pipenv
    libxml2
    libxslt.dev
    libxslt.out
  ];
  NIX_CFLAGS_COMPILE = [ "-isystem ${pkgs.libxml2.dev}/include/libxml2" ];
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ pkgs.libxml2 pkgs.libxslt.out ];
}
