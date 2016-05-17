import HTMLReportMod as rmod
import datetime
from email.MIMEImage import MIMEImage
import email.message
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import matplotlib.pyplot as plt
from time import gmtime, strftime

date = datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(1),'%Y-%m-%d')
#HTML header
title= "Yesterday Sales Trend Report - " + date
html_header = rmod.get_html_header(title)

#HTML Table1 Snapshot
dbname = 'mktplace'
query = '''select ac.c2, sum(Orders)as Orders, sum(Qty) as Qty, sum(GMV) as GMV,
sum(CB) as CB, sum(CB)/sum(GMV)*100 as 'CB%', sum(GMV)/sum(Qty) as ASP,
(sum(GMV)-(t1.gmv7/7))/(t1.gmv7/7)*100 as GMV_Trend from apparel_db.fact_apparel_sales_category fasc
join apparel_db.apparel_category ac on ac.id = fasc.category_id

left join (select c2, sum(GMV) as gmv7 from apparel_db.fact_apparel_sales_category fasc2
join apparel_db.apparel_category ac1 on ac1.id = fasc2.category_id
where fasc2.day_id between CURDATE() - INTERVAL 8 DAY and CURDATE() - INTERVAL 1 DAY
group by 1) as t1 on t1.c2 = ac.c2

where fasc.day_id between CURDATE() - INTERVAL 1 DAY and CURDATE()
group by 1 order by 4 desc;'''

query_total = '''select ac.c1, sum(Orders)as Orders, sum(Qty) as Qty, sum(GMV) as GMV,
sum(CB) as CB, sum(CB)/sum(GMV)*100 as 'CB%', sum(GMV)/sum(Qty) as ASP,
(sum(GMV)-(t1.gmv7/7))/(t1.gmv7/7)*100 as GMV_Trend from apparel_db.fact_apparel_sales_category fasc
join apparel_db.apparel_category ac on ac.id = fasc.category_id

left join (select c1, sum(GMV) as gmv7 from apparel_db.fact_apparel_sales_category fasc2
join apparel_db.apparel_category ac1 on ac1.id = fasc2.category_id
where fasc2.day_id between CURDATE() - INTERVAL 8 DAY and CURDATE() - INTERVAL 1 DAY
group by 1) as t1 on t1.c1 = ac.c1

where fasc.day_id between CURDATE() - INTERVAL 1 DAY and CURDATE()
group by 1 order by 4 desc;'''

caption = "C2 Level Sales Trend Summary"
column_names = ('C2','# of Orders','Qty','GMV','CB','CB%','ASP', 'Trend')

result = rmod.get_query_result(dbname, query)
result_total = rmod.get_query_result(dbname, query_total)
table_head1 = rmod.get_table_header(column_names, caption)

#table_data = rmod.get_table_data(result)
def get_table1_data(query_res):
    table_data = ""
    for subtuple in query_res:
        table_data = table_data + '''<tr>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0
            k+=1
            if(k>1):
                if(k in (6,8)):
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</td>"
                else:
                    table_data = table_data+'''<td  style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</td>"
            else:
                table_data = table_data+'''<td nowrap="nowrap" style="border: 2px solid black;padding: 10px;">'''+str(element)+"</td>"
        table_data = table_data + "</tr>"
    return table_data

table_data1 = get_table1_data(result)


def get_table1_total(result_total):
    table_total = ""
    for subtuple in result_total:
        table_total = table_total + '''<tr bgcolor=#E3F2FD>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0    
            k+=1
            if(k>1):
                if(k in (6,8)):
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</th>"
                else:
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</th>"
            else:
                table_total = table_total+'''<th style="border: 2px solid black;padding: 10px;">'''+str(element)+"</th>"
        table_total = table_total + "</tr>"
    table_total +="</table>"
    return table_total

table_total1 = get_table1_total(result_total)

#Creating Pie Chart

labels =()
sizes = ()
colors = ()
explode = ()
for subtuple in result:
    if(subtuple[0]=='Women Ethnic Wear'):
        labels = labels +(subtuple[0],)
        sizes = sizes + (subtuple[3],)
        colors = colors + ('#FFFF00',)
        explode = explode + (0,)
    elif(subtuple[0]=="Men's Apparel Formal & Casual"):
        labels = labels +(subtuple[0],)
        sizes = sizes + (subtuple[3],)
        colors = colors + ('#82B1FF',)
        explode = explode + (0,)
    elif(subtuple[0]=="Men's Apparel Youth"):
        labels = labels +(subtuple[0],)
        sizes = sizes + (subtuple[3],)
        colors = colors + ('#C6FF00',)
        explode = explode + (0.1,)
    elif(subtuple[0]=='WWW & Kurtis'):
        labels = labels +(subtuple[0],)
        sizes = sizes + (subtuple[3],)
        colors = colors + ('#FF9800',)
        explode = explode + (0,)
    elif(subtuple[0]=='Intimate Wear'):
        labels = labels +(subtuple[0],)
        sizes = sizes + (subtuple[3],)
        colors = colors + ('#F06292',)
        explode = explode + (0,)
    elif(subtuple[0]=='Kids Apparel'):
        labels = labels +(subtuple[0],)
        sizes = sizes + (subtuple[3],)
        colors = colors + ('#F44336',)
        explode = explode + (0.1,)    
    
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.0f%%', shadow=True, startangle=90)
# Set aspect ratio to be equal so that pie is drawn as a circle.
plt.axis('equal')
plt.title('C2 wise GMV Contributions', y=1.08, fontsize = 30)
plt.savefig('foo.png', bbox_inches='tight')


#HTML Table2 Snapshot
query = '''select ac.c2, ac.c3, sum(Orders)as Orders, sum(Qty) as Qty, sum(GMV) as GMV,
sum(CB) as CB, sum(CB)/sum(GMV)*100 as 'CB%', sum(GMV)/sum(Qty) as ASP,
(sum(GMV)-(t1.gmv7/7))/(t1.gmv7/7)*100 as GMV_Trend from apparel_db.fact_apparel_sales_category fasc
join apparel_db.apparel_category ac on ac.id = fasc.category_id

left join (select c2, c3, sum(GMV) as gmv7 from apparel_db.fact_apparel_sales_category fasc2
join apparel_db.apparel_category ac1 on ac1.id = fasc2.category_id
where fasc2.day_id between CURDATE() - INTERVAL 8 DAY and CURDATE() - INTERVAL 1 DAY
group by 1, 2) as t1 on t1.c2 = ac.c2 and t1.c3 = ac.c3

where fasc.day_id between CURDATE() - INTERVAL 1 DAY and CURDATE()
group by 1,2 order by 5 desc; '''


caption = "C3 Level Sales Trend Summary"
column_names = ('C2','C3','# of Orders','Qty','GMV','CB','CB%','ASP', 'GMV Trend')

result = rmod.get_query_result(dbname, query)
table_head2 = rmod.get_table_header(column_names, caption)

#table_data = rmod.get_table_data(result)
def get_table2_data(query_res):
    table_data = ""
    for subtuple in query_res:
        if(subtuple[8]<0):
            table_data = table_data + '''<tr bgcolor=#FFCDD2>'''
        else:
            table_data = table_data + '''<tr>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0
            k+=1
            if(k>2):
                if(k in (7,9)):
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</td>"
                else:
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</td>"
            else:
                table_data = table_data+'''<td style="border: 2px solid black;padding: 10px;">'''+str(element)+"</td>"
        table_data = table_data + "</tr>"
    table_data +="</table>"
    return table_data

table_data2 = get_table2_data(result)

#HTML footer
html_footer = rmod.get_html_footer()


#Email
subject = title
from_list = 'Arnav Mittal <arnav.mittal@paytm.com>'
cc_list = ['arnav.mittal@paytm.com']
to_list = ['apparel.category@paytm.com']

message = html_header + '''<table><tr><td style = "width: 65%" >''' + table_head1 + table_data1 + table_total1 + '''</td><td style="width: 35%"><img src="cid:image1" height="300" width="500"></td></tr></table><br>''' + table_head2 + table_data2+ html_footer

def send_email(message, subject, from_list, to_list, cc_list=[""]):
    msg = MIMEMultipart()
    #msg.attach(msgAlternative)
    msg['Subject'] = subject
    msg['From'] = from_list
    msg['To'] = ", ".join(to_list)
    msg['Cc'] = ", ".join(cc_list)
    
    
    message_html = MIMEText(message, 'html')
    fp = open('foo.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)
    
    msg.attach(message_html)
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()
    s.login('arnav.mittal@paytm.com',rmod.em_pwd)
    s.sendmail(msg['From'], to_list+cc_list, msg.as_string())
    print "Sent Mail" + strftime("%Y-%m-%d %H:%M:%S", gmtime())
    s.quit()


send_email(message, subject, from_list, to_list, cc_list)



    


