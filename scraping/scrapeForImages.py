from google_images_download import google_images_download
import sys
import os

def main(file):
    nounList = getListOfNouns(file)
    response = google_images_download.googleimagesdownload()
    print(nounList)
    for noun in nounList:
        json = {}
        json["keywords"] = noun
        json["limit"] = 7
        json["suffix_keywords"] = "white background"
        json["output_directory"] = "download"
        json["image_directory"] = "all"
        json["format"] = "jpg"
        json["size"] = "icon"
        # json["extract_metadata"] = True
        paths = response.download(json)
        key = noun + " white background"
        for count, imPath in enumerate(paths[key]):
            directory = os.path.dirname(imPath)
            if directory:
                os.rename(imPath, directory + "/" + noun + str(count) + ".jpg")






def getListOfNouns(file):
    fobj = open(file, "r")
    nounList = []
    for line in fobj:
        nounList.append(line.split(",")[0].strip())
    return nounList




if __name__ == "__main__":
    # Takes in a file that contains the nouns we're scraping for.
    main(sys.argv[1])