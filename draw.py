from PIL import Image, ImageDraw

def box(x,y):
	return [(x-50,y-50),(x+50,y+50)]
	
img = Image.open("nychase.jpg").convert("RGBA")
dot = Image.new("RGBA", img.size, (255, 255, 255, 0))
draw = ImageDraw.Draw(dot)
with open("coords.txt") as f:
	for line in f:
		x, y = map(int,line.split(","))
		draw.ellipse(box(x,y), fill = (255,255,255,128))
out = Image.alpha_composite(img, dot)
out.save("cercles.png")
