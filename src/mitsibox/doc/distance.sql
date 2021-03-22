select sum(dist) 'round distance' 
from (select ST_Distance(geo_point, lag(geo_point) OVER w, 'kilometre') as 'dist'  
      from mitsibox_boxes 
      where _id IN ('{}') window w 
      as (ORDER BY FIELD(_id,'{}'))) 
      as t".format("','".join(db.mitsibox_rounds.find("_id='00005ecb95df000000000000001d'").fields("box_list").execute().fetch_one()['box_list']),"','".join(db.mitsibox_rounds.find("_id='00005ecb95df000000000000001d'").fields("box_list").execute().fetch_one()['box_list']))