from database import *

database = Database('bestiary.db')
query = Query("monsters")
query.add_source_filter('pathfinder-bestiary')
has_darkvision = False
can_fly = False
monster_list=[]
if has_darkvision == True:
    filter_search_darkvision = '!='
else:
    filter_search_darkvision = '='
query.limit = 1
query.add_filter([MON.other_speed, '=', 'darkvision'])
data = 'system.attributes.speed.otherSpeeds'
monster_list += database.search("""SELECT data 
FROM 'monsters' m
WHERE EXISTS (
    SELECT 1 
    FROM json_tree(m.data) 
    WHERE key = 'type' AND value = 'fly'
) 
AND EXISTS ( SELECT 1 
    FROM json_tree(m.data) 
    WHERE key = 'type' AND value = 'swim'
)
AND EXISTS (
    SELECT 1 
    WHERE json_extract(m.data, '$.name') != '2' 
)
LIMIT 1
""")

for monster in monster_list:
		print(monster['name'])