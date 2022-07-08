query = "https://firebasestorage.googleapis.com/v0/b/heart-rate-monitor-cee6e.appspot.com/o/files/test.mp4?alt=media"
token = "7892b7a3-daf0-4c24-a8ee-338bc4167129.mp4"

query = query.replace("files/test", "files%2Ftest")

print(query)


