# get 1000 faces of actors and name


def store_from_page(strAdress):
    if 0:
        # python 3.x
        import urllib.request
        f = urllib.request.urlopen( strAdress )        
    else:
        import urllib
        f = urllib.urlopen(strAdress)
    page = f.read()
    print( page )
    
    """
    Page look like that:
    
<a href="/name/nm0000046/?ref_=nmls_pst"
> <img alt="Vivien Leigh"
height="209"
src="https://m.media-amazon.com/images/M/MV5BMTI2NTkwMTQ5NF5BMl5BanBnXkFtZTYwNDExNjI2._V1_UY209_CR1,0,140,209_AL_.jpg"
width="140" />
</a>        </div>
        <div class="lister-item-content">
            <h3 class="lister-item-header">
                <span class="lister-item-index unbold text-primary">76. </span>
<a href="/name/nm0000046?ref_=nmls_hd"
> Vivien Leigh
</a>            </h3>
                <p class="text-muted text-small">
                        Actress <span class="ghost">|</span>
<a href="/title/tt0044081/?ref_=nmls_kf"
> A Streetcar Named Desire
</a>                </p>
                <p>
    If a film were made of the life of Vivien Leigh, it would open in India just before World War I, where a successful British businessman could live like a prince. In the mountains above Calcutta, a little princess is born. Because of the outbreak of World War I, she is six years old the first time ...                </p>
        </div>
        <div class="clear"></div>
    </div>
    <div class="lister-item mode-detail">
        <div class="lister-item-image">
<a href="/name/nm0001401/?ref_=nmls_pst"
> <img alt="Angelina Jolie"
height="209"
src="https://m.media-amazon.com/images/M/MV5BODg3MzYwMjE4N15BMl5BanBnXkFtZTcwMjU5NzAzNw@@._V1_UY209_CR15,0,140,209_AL_.jpg"
width="140" />
</a>        </div>
        <div class="lister-item-content">
            <h3 class="lister-item-header">
                <span class="lister-item-index unbold text-primary">77. </span>
<a href="/name/nm0001401?ref_=nmls_hd"
> Angelina Jolie
</a>            </h3>

    goal: look for 
    '<a href="/name/nm0000046/?ref_=nmls_pst"
> <img alt="'

    then height="209"
src="
    
    """
    
for i in range( 10 ):
    strPage = "https://www.imdb.com/list/ls058011111/?sort=list_order,asc&mode=detail&page=%d" % (i+1)
    store_from_page( strPage )
    break
    