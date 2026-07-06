import os

for file in ["handlers/client.py", "handlers/admin.py"]:
    with open(file, "r") as f:
        content = f.read()
    
    # fix .format(id=order_id)
    content = content.replace(".format(id=order_id)", ".format(id=f\"{order_id:06d}\")")
    content = content.replace(".format(id=order_id,", ".format(id=f\"{order_id:06d}\",")
    content = content.replace("f\"#{order_id}\"", "f\"#{order_id:06d}\"")
    content = content.replace("#{order_id}", "#{order_id:06d}")
    content = content.replace("f\"#{order[0]}\"", "f\"#{order[0]:06d}\"")
    
    with open(file, "w") as f:
        f.write(content)

