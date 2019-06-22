select Encounterinfo.date,Boss.bossname, Player.playername,Class.class, Role.rolename, Guild.guildname, dps, hps, thps, aps, time, totaltime  from Encounter a
inner join Encounterinfo on a.encounterid = Encounterinfo.id
inner join Player on a.playerid = Player.id
inner join Boss on Encounterinfo.bossid = Boss.id
inner join Role on a.roleid = Role.id
inner join Guild on Encounterinfo.guildid = Guild.id
inner join Class on Player.classid = Class.id
where Encounterinfo.bossid = 1 and a.dps = (
select dps from Encounter b
inner join Encounterinfo on b.encounterid = Encounterinfo.id
where Encounterinfo.bossid = 1 and a.playerid = b.playerid
Order by b.dps desc limit 1)
Order by a.dps desc limit 20