x=0
while [[ "$x" -lt 1000 ]];do
    random=$((1 + $RANDOM % 9000))
    ((x++))
    sqlite3 users.db "insert into users values ('user$x', 'password', '$random')"
done
