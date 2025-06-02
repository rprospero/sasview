{
  # inputs.nixpkgs.url = "nixpkgs/nixos-unstable";
  inputs.nixpkgs.url = "nixpkgs/nixos-25.05";
  inputs.outdated.url = "nixpkgs/nixos-24.05";

  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";

  inputs.hatch-build-scripts.url =
    "github:rmorshea/hatch-build-scripts?ref=v1.0.0";
  inputs.hatch-build-scripts.flake = false;

  inputs.sasdata.url = "path:/home/adam/Code/sasdata";
  inputs.sasdata.inputs.nixpkgs.follows = "nixpkgs";
  inputs.sasmodels.url = "path:/home/adam/Code/sasmodels";
  inputs.sasmodels.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, outdated, pyproject-nix, sasdata, sasmodels
    , hatch-build-scripts, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        past = import outdated { inherit system; };

        project =
          pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
        python = pkgs.python312.override {
          packageOverrides = prev: super: {
            sasdata = sasdata.packages.${system}.default;
            sasmodels = sasmodels.packages.${system}.default;

            hatch-build-scripts = self.packages.${system}.hatch-build-scripts;
            hatch-sphinx = sasmodels.packages.${system}.hatch-sphinx;
            columnize = sasmodels.packages.${system}.columnize;
            siphash24 = sasmodels.packages.${system}.siphash24;

          };
        };

      in {

        # Build our package using `buildPythonPackage
        packages = {
          default = let
            # Returns an attribute set that can be passed to `buildPythonPackage`.
            attrs = project.renderers.buildPythonPackage { inherit python; };
            # Pass attributes to buildPythonPackage.
            # Here is a good spot to add on any missing or custom attributes.
          in python.pkgs.buildPythonPackage (attrs // {
            version = "v6.0.1";
            env.CUSTOM_ENVVAR = "hello";
            # nativeBuildInputs = with pkgs; [ git tinycc ];
          });
          hatch-build-scripts = python.pkgs.buildPythonPackage
            ((pyproject-nix.lib.project.loadPyproject {
              projectRoot = hatch-build-scripts;
            }).renderers.buildPythonPackage { inherit python; } // {
              version = "v1.0.0";
            });

        };

        devShells.default = let
          # Returns a function that can be passed to `python.withPackages`
          arg = project.renderers.withPackages { inherit python; };

          # Returns a wrapped environment (virtualenv like) with all our packages
          pythonEnv = python.withPackages arg;

          # Create a devShell like normal.
        in pkgs.mkShell {
          packages = [
            pythonEnv
            past.hdfview
            pkgs.ruff
            pkgs.tinycc
            pkgs.python312Packages.python-lsp-server
            pkgs.python312Packages.python-lsp-ruff
            pkgs.python312Packages.pylsp-mypy
            pkgs.python312Packages.pylsp-rope
          ];
        };
      });
}
