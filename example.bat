@echo off
:start
::Server name (This is just for the bat file)
set serverName=NoCo Gaming Cherno DayZ Server
::Server files location
set serverLocation="C:\Program Files (x86)\Steam\steamapps\common\DayZServer"
::Server Port
set serverPort=2331
::Server config
set serverConfig=serverDZ_test.cfg
::Logical CPU cores to use (Equal or less than available)
set serverCPU=2
::Sets title for terminal (DONT edit)
title %serverName% batch
::DayZServer location (DONT edit)
cd "%serverLocation%"
echo (%time%) %serverName% started.
::Launch parameters (edit end: -config=|-port=|-profiles=|-doLogs|-adminLog|-netLog|-freezeCheck|-filePatching|-BEpath=|-cpuCount=)
start "DayZ Server" /min "DayZServer_x64_test.exe" -config=%serverConfig% -port=%serverPort% "-profiles=C:\Program Files (x86)\Steam\steamapps\common\DayZServer\config_chernotest" "-servermod=" "-mod=@BaseBuildingPlus;@CF;@VanillaPlusPlusMap;@VPPAdminTools;@Code Lock;@AmmoStackBullet;@ZombieRunOverSound;@Easy Signs [by Cl0ud];@PristineRepair+;@UsefulSuppressors;@Loot Barrel Transfer;@InventoryInCar;@Gas-Pump-Refueling;@Unlimited Stamina;@OP_BaseItems;@Solar Panel Power System;@DayZ-Dog;@SchanaModGlobalChat;@SchanaModParty;@MuchFramework;@MuchStuffPack;@Ear-Plugs;@Powerstrip;@RaG_BaseItems;@Combinable Items;@RaG_Hunting_Cabin;@BodyBags;@SIX-DayZ-Auto-Run;"-cpuCount=%serverCPU% -dologs -adminlog -netlog -freezecheck
::Time in seconds before kill server process (14400 = 4 hours)
timeout 14390
taskkill /im DayZServer_x64_test.exe /F
::Time in seconds to wait before..
timeout 10
::Go back to the top and repeat the whole cycle again
goto start