{ lib, config, pkgs, ... }: with lib; {
  nix = {
    trustedUsers = [ "joerg" "root" ];
    gc.automatic = true;
    gc.dates = "03:15";
    # should be enough?
    nrBuildUsers = lib.mkDefault 32;

    daemonIOSchedClass = "idle";
    daemonCPUSchedPolicy = "idle";

    # https://github.com/NixOS/nix/issues/719
    extraOptions = ''
      builders-use-substitutes = true
      keep-outputs = true
      keep-derivations = true
      # in zfs we trust
      fsync-metadata = ${lib.boolToString (!config.boot.isContainer or config.fileSystems."/".fsType != "zfs")}
      experimental-features = nix-command flakes
    '';

    binaryCaches = [
      "https://nix-community.cachix.org"
      "https://mic92.cachix.org"
    ];

    binaryCachePublicKeys = [
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
      "mic92.cachix.org-1:gi8IhgiT3CYZnJsaW7fxznzTkMUOn1RY4GmXdT/nXYQ="
    ];
  };

  imports = [ ./builder.nix ];

  programs.command-not-found.enable = false;

  systemd.services.update-prefetch = {
    startAt = "hourly";
    path = [ config.nix.package pkgs.nettools pkgs.git ];
    script = ''
      nix build \
       --out-link /run/next-system \
       github:Mic92/dotfiles/last-build#nixosConfigurations.$(hostname).config.system.build.toplevel

      if [[ -x /home/joerg/.nix-profile/bin/home-manager ]]; then
        nix run github:Mic92/dotfiles/last-build#hm-build --  --out-link /run/next-home
      fi
    '';
  };

  nixpkgs.config.allowUnfree = true;
}
