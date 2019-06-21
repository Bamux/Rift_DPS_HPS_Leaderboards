select date, Player.playername, Player.class, Role.rolename, Guild.guildname, dps, hps, thps, aps, time, totaltime from Encounter a
inner join Player on a.playerid = Player.id
inner join Role on a.roleid = Role.id
inner join Guild on Player.guildid = Guild.id
where a.bossid = 1 and a.dps = (select b.dps from Encounter b where a.bossid = b.bossid and a.playerid = b.playerid order by b.dps desc limit 1)
Order by dps desc limit 20