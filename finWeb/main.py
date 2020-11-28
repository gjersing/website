from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def projects():
    from pandas_datareader import data
    import datetime
    from bokeh.plotting import figure, show, output_file
    from bokeh.embed import components
    from bokeh.resources import CDN

    #Grab YTD
    start=datetime.datetime(2020,1,1)
    end = datetime.datetime.now()
    tsla = data.DataReader(name="TSLA",data_source="yahoo", start=start,end=end)

    #Function to return a status value depending on open/close relationship
    def pos_neg(o,c):
        if c>o:
            value = "Positive"
        elif c<o:
            value = "Negative"
        else:
            value = "Equal"
        return value

    #Create and populate 'Status' column based on open/close relationship (+/-)
    tsla["Status"]=[pos_neg(o,c) for o,c in zip(tsla.Open, tsla.Close)]

    #Create and populate 'Middle' column with average
    tsla["Middle"]=(tsla.Open+tsla.Close)/2

    #Create and populate 'Height' column
    tsla["Height"]=abs(tsla.Open-tsla.Close)

    #Initialize graph
    p = figure(x_axis_type='datetime', width = 1000, height = 300, sizing_mode="scale_width", background_fill_color = "#2d2f2f")
    p.title.text="Tesla Stock YTD"
    p.grid.grid_line_alpha = 0.3

    hours_12 = 43200000 #Graph width milliseconds
    red = "#FF3333"
    green = "#45d96f"

    #Create high-low segments
    p.segment(tsla.index, tsla.High, tsla.index, tsla.Low, color="white")

    #Create positive rectangles [filled green]
    p.rect(tsla.index[tsla.Status=="Positive"], tsla.Middle[tsla.Status=="Positive"],
        hours_12, tsla.Height[tsla.Status=="Positive"], fill_color=green,line_color="white")

    #Create negative rectangles [filled red]
    p.rect(tsla.index[tsla.Status=="Negative"], tsla.Middle[tsla.Status=="Negative"],
        hours_12, tsla.Height[tsla.Status=="Negative"], fill_color=red, line_color="white")

    #Save components for transfer to Flask
    main, div1 = components(p)
    cdn_js = CDN.js_files[0]

    return render_template("projects.html", main=main, div1=div1, cdn_js=cdn_js)
    #Local output
    #output_file("stock.html")
    #show(p)

@app.route('/about/')
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)


#Commands for commiting to live
#heroku info | confirm login
#..\virtual\Scripts\pip install ...
#..\virtual\Scripts\pip freeze > requirements.txt
#git add .
#git commit -m "commit doc"
#git push heroku master