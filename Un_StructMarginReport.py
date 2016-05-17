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
title= "Structured vs Unstructured Margin Report - " + date
html_header = rmod.get_html_header(title)


#HTML Table5 Snapshot
dbname = 'apparel_db'
query = '''select c2, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(cb)/sum(selling_price)*100, sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date = (CURDATE() - INTERVAL 1 DAY)
group by at.order_item_id) a
group by 1 order by 3 desc;'''

query_total = '''select total, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(cb)/sum(selling_price)*100, sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, 'Total' as total, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date = (CURDATE() - INTERVAL 1 DAY)
group by at.order_item_id) a
group by 1'''

caption = "Yesterday's Margin Report - " + date
column_names = ('C2','Qty','GMV','ASP','CB%','Comm.%','CLI%', 'CM%', 'NM%')

result = rmod.get_query_result(dbname, query)
result_total = rmod.get_query_result(dbname, query_total)
table_head5 = rmod.get_table_header(column_names, caption)


def get_table5_data(query_res):
    table_data = ""
    for subtuple in query_res:
        table_data = table_data + '''<tr>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0
            k+=1
            if(k>1):
                if(k in (5,6,7,8,9)):
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</td>"
                else:
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</td>"
            else:
                table_data = table_data+'''<td nowrap="nowrap" style="border: 2px solid black;padding: 10px;">'''+str(element)+"</td>"
        table_data = table_data + "</tr>"
    return table_data

table_data5 = get_table5_data(result)

def get_table5_total(result_total):
    table_total = ""
    for subtuple in result_total:
        table_total = table_total + '''<tr bgcolor=#E3F2FD>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0    
            k+=1
            if(k>1):
                if(k in (5,6,7,8,9)):
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</th>"
                else:
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</th>"
            else:
                table_total = table_total+'''<th style="border: 2px solid black;padding: 10px;">'''+str(element)+"</th>"
        table_total = table_total + "</tr>"
    table_total +="</table>"
    return table_total

table_total5 = get_table5_total(result_total)





#HTML Table6 Snapshot
dbname = 'apparel_db'
query = '''select c2, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(cb)/sum(selling_price)*100, sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 DAY ,'%Y-%m-01')
group by at.order_item_id) a
group by 1 order by 3 desc;'''

query_total = '''select total, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(cb)/sum(selling_price)*100, sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, 'Total' as total, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 DAY ,'%Y-%m-01')
group by at.order_item_id) a
group by 1'''

caption = "MTD Apparel Margin Report"
column_names = ('C2','Qty','GMV','ASP','CB%','Comm.%','CLI%', 'CM%', 'NM%')

result = rmod.get_query_result(dbname, query)
result_total = rmod.get_query_result(dbname, query_total)
table_head6 = rmod.get_table_header(column_names, caption)


def get_table6_data(query_res):
    table_data = ""
    for subtuple in query_res:
        table_data = table_data + '''<tr>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0
            k+=1
            if(k>1):
                if(k in (5,6,7,8,9)):
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</td>"
                else:
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</td>"
            else:
                table_data = table_data+'''<td nowrap="nowrap" style="border: 2px solid black;padding: 10px;">'''+str(element)+"</td>"
        table_data = table_data + "</tr>"
    return table_data

table_data6 = get_table6_data(result)

def get_table6_total(result_total):
    table_total = ""
    for subtuple in result_total:
        table_total = table_total + '''<tr bgcolor=#E3F2FD>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0    
            k+=1
            if(k>1):
                if(k in (5,6,7,8,9)):
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</th>"
                else:
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</th>"
            else:
                table_total = table_total+'''<th style="border: 2px solid black;padding: 10px;">'''+str(element)+"</th>"
        table_total = table_total + "</tr>"
    table_total +="</table>"
    return table_total

table_total6 = get_table6_total(result_total)



#HTML Table1 Snapshot
dbname = 'apparel_db'
query = '''select c2, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(cb)/sum(selling_price)*100, sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date = (CURDATE() - INTERVAL 1 DAY)
group by at.order_item_id) a
where a.is_structured = 1
group by 1 order by 3 desc;'''

query_total = '''select total, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(cb)/sum(selling_price)*100, sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, 'Total' as total, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date = (CURDATE() - INTERVAL 1 DAY)
group by at.order_item_id) a
where a.is_structured = 1
group by 1'''

caption = "Structured Margin Report - " + date
column_names = ('C2','Qty','GMV','ASP','CB%','Comm.%','CLI%', 'CM%', 'NM%')

result = rmod.get_query_result(dbname, query)
result_total = rmod.get_query_result(dbname, query_total)
table_head1 = rmod.get_table_header(column_names, caption)


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
                if(k in (5,6,7,8,9)):
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</td>"
                else:
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</td>"
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
                if(k in (5,6,7,8,9)):
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</th>"
                else:
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</th>"
            else:
                table_total = table_total+'''<th style="border: 2px solid black;padding: 10px;">'''+str(element)+"</th>"
        table_total = table_total + "</tr>"
    table_total +="</table>"
    return table_total

table_total1 = get_table1_total(result_total)

#HTML Table2 Snapshot
query = '''select c2, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date = (CURDATE() - INTERVAL 1 DAY)
group by at.order_item_id) a
where a.is_structured = 0
group by 1 order by 2 desc;'''

query_total = '''select total, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, 'Total' as total, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date = (CURDATE() - INTERVAL 1 DAY)
group by at.order_item_id) a
where a.is_structured = 0
group by 1 '''

caption = "Unstructured Margin Report - " + date
column_names = ('C2','Qty','GMV','ASP','Comm.%','CLI%', 'CM%', 'NM%')

result = rmod.get_query_result(dbname, query)
result_total = rmod.get_query_result(dbname, query_total)
table_head2 = rmod.get_table_header(column_names, caption)


def get_table2_data(query_res):
    table_data = ""
    for subtuple in query_res:
        table_data = table_data + '''<tr>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0
            k+=1
            if(k>1):
                if(k in (5,6,7,8)):
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</td>"
                else:
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</td>"
            else:
                table_data = table_data+'''<td nowrap="nowrap" style="border: 2px solid black;padding: 10px;">'''+str(element)+"</td>"
        table_data = table_data + "</tr>"
    return table_data

table_data2 = get_table2_data(result)

def get_table2_total(result_total):
    table_total = ""
    for subtuple in result_total:
        table_total = table_total + '''<tr bgcolor=#E3F2FD>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0    
            k+=1
            if(k>1):
                if(k in (5,6,7,8)):
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</th>"
                else:
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</th>"
            else:
                table_total = table_total+'''<th style="border: 2px solid black;padding: 10px;">'''+str(element)+"</th>"
        table_total = table_total + "</tr>"
    table_total +="</table>"
    return table_total

table_total2 = get_table2_total(result_total)


#Line Chart GMV Contributions

query = '''select order_date, U/T*100, S/T*100 from (select order_date, 
sum(case when is_structured = 0 then selling_price else 0 end) as U,
sum(case when is_structured = 1 then selling_price else 0 end) as S,
(sum(case when is_structured = 0 then selling_price else 0 end) + sum(case when is_structured = 1 then selling_price else 0 end)) as T
from apparel_db.apparel_transactions at
where order_date between CURDATE() - INTERVAL 7 DAY and CURDATE() group by 1)a
group by 1;'''

result = rmod.get_query_result(dbname, query)

dategmv = ()
structgmv = ()
unstructgmv = ()

for subtuple in result:
    k=0
    for element in subtuple:
        k+=1
        if(k==1):            
            dategmv = dategmv + (element,)
        elif(k==2):
            unstructgmv = unstructgmv + (element,)
        elif(k==3):
            structgmv = structgmv + (element,)

plt.plot(dategmv, unstructgmv, marker='o', label='Unstructured')
plt.plot(dategmv, structgmv, marker='D', label='Structured')

plt.xlabel('Date')
plt.ylabel('GMV Contribution %')

plt.title('Un/Structured GMV Contribution')
plt.legend()

plt.savefig('SvU_GMVContribution.png', bbox_inches='tight')

plt.clf()

#Line Chart CM%

query1 = '''select order_date, (sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 from (select at.order_item_id, order_date, ac.c1, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
where at.order_date between CURDATE() - INTERVAL 7 DAY and CURDATE()
group by at.order_item_id) a
where a.is_structured = 1
group by 1'''

query2 = '''select order_date, (sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 from (select at.order_item_id, order_date, ac.c1, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
where at.order_date between CURDATE() - INTERVAL 7 DAY and CURDATE()
group by at.order_item_id) a
where a.is_structured = 0
group by 1'''

query3 = '''select order_date, (sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 from (select at.order_item_id, order_date, ac.c1, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
where at.order_date between CURDATE() - INTERVAL 7 DAY and CURDATE()
group by at.order_item_id) a
group by 1'''

result1 = rmod.get_query_result(dbname, query1)
result2 = rmod.get_query_result(dbname, query2)
result3 = rmod.get_query_result(dbname, query3)

datecm1 = ()
datecm2 = ()
datecm3 = ()
apparelcm = ()
structcm = ()
unstructcm = ()

for subtuple in result1:
    k=0
    for element in subtuple:
        k+=1
        if(k==1):            
            datecm1 = datecm1 + (element,)
        elif(k==2):
            structcm = structcm + (element,)
        
for subtuple in result2:
    k=0
    for element in subtuple:
        k+=1
        if(k==1):            
            datecm2 = datecm2 + (element,)
        elif(k==2):
            unstructcm = unstructcm + (element,)

for subtuple in result3:
    k=0
    for element in subtuple:
        k+=1
        if(k==1):            
            datecm3 = datecm3 + (element,)
        elif(k==2):
            apparelcm = apparelcm + (element,)
plt.plot(datecm2, unstructcm, marker='o', label='Unstructured')
plt.plot(datecm1, structcm, marker='D', label='Structured')
plt.plot(datecm3, apparelcm, marker='*', linestyle='--', color='r', label='Total')


plt.xlabel('Date')
plt.ylabel('Last 7 days CM%')

plt.title('Un/Structured CM%')
plt.legend()


plt.savefig('SvU_CM7.png', bbox_inches='tight')




#HTML Table3 Snapshot
query = '''select c2, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(cb)/sum(selling_price)*100, sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 DAY ,'%Y-%m-01')
group by at.order_item_id) a
where a.is_structured = 1
group by 1 order by 3 desc;'''

query_total = '''select total, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(cb)/sum(selling_price)*100, sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, 'Total' as total, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 DAY ,'%Y-%m-01')
group by at.order_item_id) a
where a.is_structured = 1
group by 1 order by 3 desc;'''

caption = "MTD Structured Margin Report"
column_names = ('C2','Qty','GMV','ASP','CB%','Comm.%','CLI%', 'CM%', 'NM%')

result = rmod.get_query_result(dbname, query)
result_total = rmod.get_query_result(dbname, query_total)
table_head3 = rmod.get_table_header(column_names, caption)


def get_table3_data(query_res):
    table_data = ""
    for subtuple in query_res:
        table_data = table_data + '''<tr>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0
            k+=1
            if(k>1):
                if(k in (5,6,7,8,9)):
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</td>"
                else:
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</td>"
            else:
                table_data = table_data+'''<td nowrap="nowrap" style="border: 2px solid black;padding: 10px;">'''+str(element)+"</td>"
        table_data = table_data + "</tr>"
    return table_data

table_data3 = get_table3_data(result)

def get_table3_total(result_total):
    table_total = ""
    for subtuple in result_total:
        table_total = table_total + '''<tr bgcolor=#E3F2FD>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0    
            k+=1
            if(k>1):
                if(k in (5,6,7,8,9)):
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</th>"
                else:
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</th>"
            else:
                table_total = table_total+'''<th style="border: 2px solid black;padding: 10px;">'''+str(element)+"</th>"
        table_total = table_total + "</tr>"
    table_total +="</table>"
    return table_total

table_total3 = get_table3_total(result_total)

#HTML Table4 Snapshot
query = '''select c2, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 DAY ,'%Y-%m-01')
group by at.order_item_id) a
where a.is_structured = 0
group by 1 order by 2 desc;'''

query_total = '''select total, sum(qty), sum(selling_price), sum(selling_price)/sum(qty), sum(commission)/sum(selling_price)*100, sum(shipping_amount)/sum(selling_price)*100, 
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price))*100 as cm,
(sum(commission)/sum(selling_price) + sum(shipping_amount)/sum(selling_price) - sum(cb)/sum(selling_price) + sum(mli)/sum(selling_price) - sum(lc)/sum(selling_price))*100 as nm
from (select at.order_item_id, 'Total' as total, ac.c2, is_structured, qty, selling_price, cb, shipping_amount,
sum(if(commission_meta_id = 2,sor.amount,0))/1000 + sum(if(commission_meta_id = 3,sor.amount,0))/1000 as commission,
sum(if(commission_meta_id = 4,sor.amount,0))/1000 as mli, 
IFNULL(CASE WHEN m.lmd_enabled = 0 THEN 0 ELSE IFNULL((qty * lc.avg_item_freight),(dcf.avg_item_freight * qty)) END,0) as lc
from apparel_db.apparel_transactions at
join payouts.sales_order_revenue sor ON sor.direction = 1 and at.order_item_id = sor.order_item_id
join apparel_db.apparel_category ac on ac.id = at.category_id
LEFT JOIN logistics.productwise_freight lc ON lc.product_id = at.product_id 
LEFT JOIN logistics.categorywise_freight dcf ON dcf.category_id = at.category_id 
LEFT JOIN mktplace.merchant m ON m.id = at.merchant_id
where at.order_date >= DATE_FORMAT(CURDATE() - INTERVAL 1 DAY ,'%Y-%m-01')
group by at.order_item_id) a
where a.is_structured = 0
group by 1'''

caption = " MTD Unstructured Margin Report"
column_names = ('C2','Qty','GMV','ASP','Comm.%','CLI%', 'CM%', 'NM%')

result = rmod.get_query_result(dbname, query)
result_total = rmod.get_query_result(dbname, query_total)
table_head4 = rmod.get_table_header(column_names, caption)


def get_table4_data(query_res):
    table_data = ""
    for subtuple in query_res:
        table_data = table_data + '''<tr>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0
            k+=1
            if(k>1):
                if(k in (5,6,7,8)):
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</td>"
                else:
                    table_data = table_data+'''<td style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</td>"
            else:
                table_data = table_data+'''<td nowrap="nowrap" style="border: 2px solid black;padding: 10px;">'''+str(element)+"</td>"
        table_data = table_data + "</tr>"
    return table_data

table_data4 = get_table4_data(result)

def get_table4_total(result_total):
    table_total = ""
    for subtuple in result_total:
        table_total = table_total + '''<tr bgcolor=#E3F2FD>'''
        k=0
        for element in subtuple:
            if(element == None):
                element=0    
            k+=1
            if(k>1):
                if(k in (5,6,7,8)):
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_percentage(element)+"</th>"
                else:
                    table_total = table_total+'''<th style="border: 2px solid black; text-align: right; padding: 10px;">'''+rmod.format_num(element)+"</th>"
            else:
                table_total = table_total+'''<th style="border: 2px solid black;padding: 10px;">'''+str(element)+"</th>"
        table_total = table_total + "</tr>"
    table_total +="</table>"
    return table_total

table_total4 = get_table4_total(result_total)





html_footer = rmod.get_html_footer()

#Email
subject = title
from_list = 'Arnav Mittal <arnav.mittal@paytm.com>'
#to_list = ["suminder.singh@paytm.com"]
#cc_list=["arnav.mittal@paytm.com"]
to_list = ["arnav.mittal@paytm.com"]
cc_list=["arnav.mittal@paytm.com"]


#to_list = ['suminder.singh@paytm.com', 'arun.gaur@paytm.com', 'abhishek.das@paytm.com', 'aditya1.jain@paytm.com','varun.gupta@paytm.com', 'shuchi.mittal@paytm.com', 'smita.ray@paytm.com',  'manisha.kashyap@paytm.com', 'ankita.banerjee@paytm.com']
#to_list = ['apparel.category@paytm.com']
message = html_header + '''Report contains data only for orders acknowledged by merchants.''' + '''<table><tr><td  valign="top">''' +  table_head5 + table_data5 + table_total5 + '''</td><td valign="top"> ''' + table_head6 + table_data6 + table_total6 + '''</td></tr><tr><td><br></td><td><br></td></tr><tr><td valign="top">'''   + table_head1 + table_data1 + table_total1 + '''</td><td valign="top"> ''' + table_head2 + table_data2 + table_total2 + '''</td></tr><tr><td><br></td><td><br></td></tr><tr><td align="center"><img src="cid:image1" height="300" width="620"></td align="center"><td><img src="cid:image2" height="300" width="620"></td></tr>''' + '''<tr><td  valign="top">''' + table_head3 + table_data3 + table_total3 + '''</td><td valign="top"> ''' + table_head4 + table_data4 + table_total4 + '''</td></table>''' +html_footer


def send_email(message, subject, from_list, to_list, cc_list=[""]):
    msg = MIMEMultipart()
    #msg.attach(msgAlternative)
    msg['Subject'] = subject
    msg['From'] = from_list
    msg['To'] = ", ".join(to_list)
    msg['Cc'] = ", ".join(cc_list)
    message_html = MIMEText(message, 'html')
    fp = open('SvU_GMVContribution.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)
    fp = open('SvU_CM7.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image2>')
    msg.attach(msgImage)
    
    msg.attach(message_html)
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()
    s.login('arnav.mittal@paytm.com',rmod.em_pwd)
    s.sendmail(msg['From'], to_list+cc_list, msg.as_string())
    print "Sent Mail" + strftime("%Y-%m-%d %H:%M:%S", gmtime())
    s.quit()


send_email(message, subject, from_list, to_list, cc_list)



