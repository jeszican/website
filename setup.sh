# script to restart game

admin_team_code=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 20 | head -n 1)

# clear the teams
echo "DELETE FROM teams;" | sqlite3 ./ctf/db
# clear all users
echo "DELETE FROM users;" | sqlite3 ./ctf/db
# insert the admin team
echo "INSERT INTO teams values(1,'Administrators','${admin_team_code}',0,'','','');" | sqlite3 ./ctf/db
# delete all challenges
echo "DELETE FROM challenges;" | sqlite3 ./ctf/db
