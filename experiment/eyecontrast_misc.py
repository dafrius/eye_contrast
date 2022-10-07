# %% Pulling images out, putting them in a variable
# We take all the images in the folder and put them in a list
imlist=os.listdir(os.path.join(stimPath))
masklist=os.listdir(os.path.join(maskPath))
ims=[]
ims2=[]
#we create the new variable, called ims, which contains all the pixel information of all the images
for i in range(0, len(imlist)):
    ims.append(Image.open(os.path.join(stimPath,imlist[i]), mode="r"))
    ims2.append({'imname':imlist[i],'image':Image.open(os.path.join(stimPath,imlist[i]), mode="r")})
# we convert it into numpy arrays
ims = np.array([np.array(im) for im in ims])

praclist= os.listdir(os.path.join(pracPath))
pracmasklist=os.listdir(os.path.join(pracmaskPath))
pracims=[]
pracims2=[]

for i in range(0,len(praclist)):
    pracims.append(Image.open(os.path.join(pracPath, praclist[i]), mode="r"))
    pracims2.append({'imname':praclist[i],'image':Image.open(os.path.join(pracPath,praclist[i]), mode="r")})


