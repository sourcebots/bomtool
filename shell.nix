with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "sb-bomtool-env";
  buildInputs = [
    pipenv
    libxml2
    libxslt
  ];
  NIX_CFLAGS_COMPILE = [ "-isystem ${libxml2.dev}/include/libxml2" ];
}
