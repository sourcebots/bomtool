with import <nixpkgs> {};

let
  ratelimit = python3Packages.buildPythonPackage rec {
    version = "2.2.0";
    pname = "ratelimit";
    src = fetchFromGitHub {
      owner = "tomasbasham";
      repo = "ratelimit";
      rev = "v${version}";
      sha256 = "0kyn5p45ylyx46sprk6s2rqpnwmiwz4i3zgmnzvgmfva5rbx5qzn";
    };
  };

  wimpy = python3Packages.buildPythonPackage rec {
    version = "0.6";
    pname = "wimpy";
    src = fetchFromGitHub {
      owner = "wimglenn";
      repo = "wimpy";
      rev = "v${version}";
      sha256 = "1d233bhbsbrixsrgaay3h97vx9jcdb73645bgjs0r3fdi6lnksnr";
    };
  };

in python3Packages.buildPythonPackage rec {
  version = "0.1";
  pname = "sb-bomtool";
  src = ./.;
  propagatedBuildInputs = with python3Packages; [
    beautifulsoup4
    pyyaml
    ratelimit
    requests
    xlrd
    wimpy
    zeep
  ];
}
