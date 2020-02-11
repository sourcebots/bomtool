{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  name = "sb-bomtool-env";
  buildInputs = with pkgs; [
    python3
    libxml2
    libxslt.dev
    libxslt.out
  ];
  NIX_CFLAGS_COMPILE = [ "-isystem ${pkgs.libxml2.dev}/include/libxml2" ];
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ pkgs.libxml2 pkgs.libxslt.out ];
}
