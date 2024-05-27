import random
import wx
import wx.lib.agw.aui as aui
from wx.lib.embeddedimage import PyEmbeddedImage


Mondrian = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAHFJ"
    "REFUWIXt1jsKgDAQRdF7xY25cpcWC60kioI6Fm/ahHBCMh+BRmGMnAgEWnvPpzK8dvrFCCCA"
    "coD8og4c5Lr6WB3Q3l1TBwLYPuF3YS1gn1HphgEEEABcKERrGy0E3B0HFJg7C1N/f/kTBBBA"
    "+Vi+AMkgFEvBPD17AAAAAElFTkSuQmCC")

# Custom pane button bitmaps
# ----------------------------------------------------------------------
close = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAh9J"
    b"REFUKJFl0s1LFGEAx/HvMzO7M9vmrrSuThJIhslmaSZqFgZLdSqKjr147VB/Qn9Af0GXTiIU"
    b"vVAQdRAKqkuColaiiyiKr7FKL7u6OzM78zxPh6igfvcvv8tHCMMEoHAxr/35AlpK/p0wTZz2"
    b"HLlXbwWABTBzrk83DnSRvjWE4Tj/Rcr3KU1/Zsav6GNvxoU1cSGvmwZ7SZ3Oo5MpIiuGrvl/"
    b"X+IOIgpJndmPNONM2Elt7KyuU9/djySCbBNGo4ssriA3FlHfNjAaXchkiSKf+u5+ykvLGHLP"
    b"XlQiSS0SqLoMosHF6DwJdfWIXC+iwUWls4TaQtkJQtPC8gIPo1pldvQlanGNnqs3iLktyOwB"
    b"TNMk9AMmnzzEmHjHiVOD7AQBVjUI0JUdDqaTzLwfZS6VovPSFUytQUrmXjynfO8uR9MWyrEJ"
    b"/QCrFkrU9leM5QVysoa044jSD9AAmoxjk6GKtbqNaukglAojCHyi8Q8Ec7PsO3sZt/UQ3uYG"
    b"3+cLeF82cdsOk719hyjlIis+Na0wlJRExSJe23EitwW5VWRqZJjHQ9eYGhlGbhWJmlvxOvqp"
    b"lXeRSmM57TnWSx4/ltZZsR5hOAlKz57St1tmbWSYscou0vNIfJwlyGRIHOlACMPkwUCPzsmQ"
    b"aswi8Hza/ICYgFDDgmMTd2ySkaRgxrg+NinEb3v3z+f15qdpQt/DQvwREaGJOQmau7q5+fqX"
    b"vZ+3DPNuDe9/tAAAAABJRU5ErkJggg==")

# ----------------------------------------------------------------------
close_inactive = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAh5J"
    b"REFUKJFl0stLVFEAgPHv3Htn7lzNGW1GZzSNtJI0fFZjQkQPqV0U0SJmnZugP6B9/0O4cZNE"
    b"ZFAQUdBrlZBYoJmGOYSPSUvRRp25r3NOi8iN3/7b/YQwTAAuDn7VM3kXqdiTaUBbS4w3Q+0C"
    b"QAjDpD83qfuPNdDZEicWMfZMbqCYzBcZmy0wNtIprIFb4/pUa4bzfXHiVRAxFWVP7w6OLQgk"
    b"NDTFsWOKyopxbSyubpPtShB6mroaQTolWFiQzM9LCsuadEpQWw1uSZHtSpBfKmLscySVFRpM"
    b"j+R+SaZWcLrXoDoBJ7shUydIJRVW1MeJaSwzxHLLJUqu4PnLaZYKity1Hg42RjhQb2CaAs/z"
    b"efjsM+/GDM6e6cErF7Hc8g5bO5rKqmZevJ8iXjXL1csdaC2QoeDpq1nu3S8SiXZgJxWe72NJ"
    b"6bO+rZhbNvDDdqKOZHMHtBYARJ0UrkyysGRyfEuhVIDhej4fpkO+5H2uXKqm5VCawi+fbz82"
    b"+fnb4+jhNHdvp8jUh7ihRMkAQ0rF6oaku73EwfqQlbWQ4dEJbt55xPDoBCtrIc2NIX3dZbbd"
    b"AK0k4lzugS5HT7C+vkG2tYxjmzx++4eiaiJuLHLjQoKSKxmfc0gma3D8iX8istdHtG+3YVHC"
    b"dX28yBEQEdABdvAd244iRQVRb4aPT3JC/Lc3kBvSn6YKlL0AYVi7IrQKcewIvR0NvB4ZFAB/"
    b"Aa4X7YpTOtu/AAAAAElFTkSuQmCC")

# ----------------------------------------------------------------------
maximize = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAJZJ"
    b"REFUKJG9kj0OwjAMRp8D6hDUExDmrr0dEkOHXgXuAMfIBl1yCwaMMAyoIJQWqUu/yZa/5x/J"
    b"Im7BVLnJBLDsg2vbPC3G8e51zapp5QeyGLHzBYbWtcfwJFlv8Nsdrqpypuu4HfY5hHPgPVKW"
    b"+STv3/XeOnrEH80HfW9SxVIaNFlKoJpDEgL30xGKIqdUkRA+qcz2Ri8+yyNzplbFQwAAAABJ"
    b"RU5ErkJggg==")

# ----------------------------------------------------------------------
maximize_inactive = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAJhJ"
    b"REFUKJFjZGRiZiAVMJGsg4GBgQXGaGz7+v/CxX84FRroMzHUV3Ezomi6cPEfw/Vb/xiYsbj2"
    b"718cNsnKMDJUlnAwqKthuvjmrX8MS1b8xtTEyMTAwMXFyMDLw4ihiYuLkYERySyyAoJ+muB+"
    b"+v2bgeHeA+xBfu/BP4bfiHBAaJKWYmTYsfsPAysrpqbfvyHyMMBIt2QEAFPtI359ud6yAAAA"
    b"AElFTkSuQmCC")

# ----------------------------------------------------------------------
minimize = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAMlJ"
    b"REFUKJGdkrsNwkAQRN/eWohPByYkQaIKSqAJhBAF0AdExGRUQwoioAREAth3S2BjWzLIwER7"
    b"oxntzOpEnPIrotcQ1lvjeIbbHXjkpAczkAf0OjAc4GZTQZwiTrHNzhoxX5g4xRU7U9+c654A"
    b"VEzY150qpuQLedY1qvFJCqrgX3ENQp5C7IMp9eAEQsjEIWQXVC3UpckSWK5gfwCRnKv0nIwL"
    b"vrLJQDzomytGEXRb5bOYLhfotyEeASk1xfUEcT+r9s83cs2SOp6D2FytkDyOCgAAAABJRU5E"
    b"rkJggg==")

# ----------------------------------------------------------------------
minimize_inactive = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAANRJ"
    b"REFUKJGdkj1OgkEQhp/ZJSCF0VBYmUBPixfwAtzRS2DvCShMvAGRUJCQkMjOjwV8CwT1C77V"
    b"zGaevO9MViRlrlWnKd7el7HaKGpgpQDg7ng4rkY3Bw/3PZ4nI6lQzpnp0+BPh5fXDwBS8+DR"
    b"HquonUNEOxWHmaOTWSvk6sDJIRqZO0kEO8nrAUmEiN8gC8iCHyBvYqdU01RIizKbr1msy4/R"
    b"xo/9uvbRKYIIJewSSgIderWv0PZrRzcrw9tAVeulwvd7fC62DO5uAJD/fKPUPnKpbzVEY0DN"
    b"U2N1AAAAAElFTkSuQmCC")

# ----------------------------------------------------------------------
restore = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAUlJ"
    b"REFUKJGd0j9LW1EYBvDfvUkM1iaGkohaKJRQv0XJ5FCKg1PnoogUHCwOjnVTx67d2n6Cgq2O"
    b"7oXupdKhUIOQqMRSE733djiXNkoXPcvhvO/z530fThTFBTc9RUjfvM2020zeC5VS3i3kiBg/"
    b"ulQa4oXnUREcd9nZ5fAnvQ5nHaKEYkY14w4eNHm6+M9JfTwQHs5w2WdjHSkRBj2W5uge8Ghi"
    b"iBQl/O6RXDA9gUvWXnJ8xIdPYdQIpXiIVMJpm433tB4H0OcvLMwHxyzoSIeCUEB5QJywvUm/"
    b"T6vFk2dUavxC5Vp6RlDLya+3ODnBK4p3ebfC4D+RK2AM/TP29slSqjVerPJxJ/RG/6LzK00p"
    b"Y2UuqF7gHD2Mo5ELX3H62uZ+k85BWDbJF6/nIZUx1eR7d4hUnWR2mZn61eHztEQp344oN8Lz"
    b"Nn/vD5FAXWAC04u0AAAAAElFTkSuQmCC")

# ----------------------------------------------------------------------
restore_inactive = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAYxJ"
    b"REFUKJGdkr2PTGEUh5/z3ntndmYXIyODiI8oVyGRLTUitpToNCRCJdv7B2gkOrV6Q4hWp6JV"
    b"jXILhWKHeMfcmXvfj3MUk7jbcqrTPPk9J+cn4gr+dUqAz9OFzWth0CtJCiEaWUHNiMnIahQ0"
    b"TEYF16+OpARYto6v35SZj/gaZnNj2UIblZlX6lXg8thzf/dYl7RRFfyYK2fHjskI9m6XZIWs"
    b"4Gtj72VkerAk5SEADiBEWKwEVeHEphASvPoQefq65fRJAdaqmHVQG43vP5XdawX3blZcueh4"
    b"/qjPqeMQsxEUytKoSu30YjZmXlkFeP8p0URj+0LBrZ2KrYGjpiBlR1bpoDYYhz6Ts7H/MTJv"
    b"4O4NWIhj/03AZ0hBCNl1UMjCrxr80nj2oI8qbA2FJ28j774oMQnWGqpH/qQ5s2paHr6IbPSg"
    b"KoTWCYfZcMGhvqHQjGAd5Ehsn/FMD35Ti6NXClnWOiFCkRI7lxKD/pGbzk96PL4zJoUhhvyt"
    b"S7L1bmpUpXBusgmA/E/3/gASuMtl4Uj5YAAAAABJRU5ErkJggg==")

# ----------------------------------------------------------------------

fullscreen = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAActJ"
    b"REFUOI2dk09I02EYx7/v+/7+DDRRYg4EWWYUKAjDSxBhJKuEUUJslwi8BXoaEaIdhpchddgt"
    b"CKIgCIbeYmXaTHboEigZ5GENdCCKfyZKTrf5+72Pp7nf9Lcf4gPP5fl+3i9feJ8HcKrghPD4"
    b"X9c5IdxJvHq4PFKvy3dOjKgltN4f71QU/lGo4kZD250/u5nZtB3H7IY9PRElW6f/ApgPAIiw"
    b"YZpax+rM8x2nNBeqSoLghMBkyIzFYptSSrcdzDnfCofDzd3db9X5+WdHAKAAQEt/9LKaz3zI"
    b"Ag+llG7f7UeQks4YLP787AaAnGdn2PsgupD9NvpVaeuLXmeGMkcwm8rg2tYe4tOLVY+D/i5L"
    b"EtYoQQlvIDqoEKgfoGbGmVEGHt/tQOBWe5WBrut4k05VTAQHA4b4ytTLVyAMSML/smgYBorF"
    b"YlUbxok/TEkmZ/zHfkHc5ACw/GX4E0B+q4GmaVVtNYBEPOPL39v4/iJ/Zg/O8wvWme0iIRLh"
    b"3t9osI6u7GI/lRozTqP2t7DUyVjJlWQlV46VXDl+5FpIX4Jmm8rWYDJkEmNPhSoKqqYUJKcn"
    b"64mxAzu05jHt/UtuN17rJSL6u5IYeV+LOwbQBrHjq9vsKwAAAABJRU5ErkJggg==")

# ----------------------------------------------------------------------
reload = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAApFJ"
    b"REFUOI11k72LXFUUwH/n3vvmvbzZnZnNl7sWI0mIISaIIKYJ2AmbznQWKezSiOm0NaXpAjZu"
    b"kQTMHyBC0JBOCwmyWBrXHaMmuopLdt7Ox3vz3r33WMyyCJscOBwOnPPjfAovEFWEr2kBcIla"
    b"BH1enBxI/Golb7ZGb/kZb6vXkyCI4VeX8G3iFn+Qq1vTFwL0886pcqofNSXvgh41qEGEqBJR"
    b"tl3Gl2ZBbhy6ujs4ACjXuidiET7zDauuhRFnidky0gwxfkz0gq+JJuEbl9kPDn1YPAYwAHqT"
    b"VEfhmq9ZdS4aJBIWThNeuUQ4fpEgbbAGk3dMbMxqqMI1vUkK4AAa8vN+ppdj96ypj59DJv+g"
    b"+TJiFtDuq2iIUO1A1sM8/c7Epr48Nd0voFifAxpzAQ0rdPuEi5/M+6rHaLkDf3yPWzqLOAfT"
    b"f8G20KZeCT5cANaNKoJKX4RExluIr5B8CXp9aCrsbHvuJ2201SGaNiKaaJS+KmJE0KjRIwZm"
    b"BZTP5gvXiHRWiJ3+vFObQdqD7AiIQIxeBHUAorqh1lWiIWP3TyiHkPXgpdfg5Dv4jXvY0S9g"
    b"LGoyRGyFbzb2hxiCfWgdA2M5J5v3sVRodpQg78GRU5B2MX89BT9Bmm1i1MFM7cP9NXZmo83Q"
    b"hNvEokzKAdZaEuNxjx8gj+6RDB9h8iWME/DDMlbh9jFGm/sAuU7UkbsVxuM1KX+fGgokzUlS"
    b"S1o9wbUMRgvYHUxDsbsmtbsl14kHTvnZx0td0vqKW2y/b7vLZ6R9LAfQyfY0DLd+nhWTO9a3"
    b"7h7+dKd43i8I0Hp5kYUrr7vTbyzzZq8tJwB2xvrbj09Yv/uT3/x7zBiYwcEKBEiBfM/aPQUI"
    b"ewk1MPk/4D/OAyg6YvZkywAAAABJRU5ErkJggg==")

# ----------------------------------------------------------------------
remove = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAApVJ"
    b"REFUOI2lkUtIVHEUxr//vf9778x4J8d8DDaODjo+mBzLKFJJJbVWFdmiVaEtehBYi2hVENXK"
    b"XS0iC6JNFkbkInwVQeoiiLAHtlAhW6TjTPnA9DreO/d/WjjOIkiDDnxwFuc7fOd3gP8s+bmD"
    b"118+UPGmiagsNL88UJqb62gLhTrP1tVdmY5G334zjOiGG574XF00/IjmHt6lO+mujvvb/J1L"
    b"3d1k9vRQk9fbsWkCX9ya/DIxUdVQ2+gt9Obt3lG1N6ykp+NGe/vnl5OT15aEiGx6x03g4GBl"
    b"IEGX2ojaLlBXeflKXWbm/n9i8BTILivgV4vkuXC0/x0W3n9C3tYMnsjOXpmyrMEfhmFutIC7"
    b"s3C9Jpw4vjAO3Ha6zS2Ki11cNZXz+fnnXkUiMbuy8l6OrreYpikxxgVRQmKMyaqa9mJo6PUH"
    b"PhTc6Q9gDvM1u1BxuFVxKRK+9/UhOjaOiCzL24uLHzcfOlLvcGoAGDRNgSxz9PcPnIrHf9Xy"
    b"r6FqHm85gXBFCNUeDwMAo7EB77uewdHxIBLI85c3HzsKp9MJxhgYYwCAmZmZwOjoWBp3EbJz"
    b"SoPQPR5YpglbCLhcaQgEg/Do6XsWF1elkZGPUFUVkiRB0zTouo7p6Rh03bOPBwKBUIbbDQAg"
    b"AIwxmKYJb1YWTp9pPckkSYrFfoKIUgKAkpIgDMO6xX0+n+R0OSGESJG1LAv5BX4UBQulRCIB"
    b"y7Jg2zaEsGHbAkQCmqZifn7JwYlk+vM1jDEIIWAYBoQQSbNIiYggxCqEYDZXFDVlWge03v9N"
    b"azMEzjm4qqp83STLUvJGAmMEYM1AxFLpkgggSYCiaDKPRhenenuHddNM0BokgMhODq+DQyo6"
    b"QLBtgiwzNju7svwbnlAlxKIQCyQAAAAASUVORK5CYII=")

# ----------------------------------------------------------------------
sort = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAMdJ"
    b"REFUOI2VklEOgyAMhv+iR1jmdfQWHt1dQXA+dI9K97BpaIFE/4SQAv36UwC5BukAROxaOl7T"
    b"pPYdbmpZVxUrgMRNyLUkcZMqIIQ64IpCWMqAo6qdrbyfVdymAbmWLDAH+LKDq6oC0uql+FDw"
    b"uonnFWLcM8vONRkkLBWATSgBAeBt/gH9fp9WjLvY6t3zIZIiCZjnQFkTS8kA0PcDmBn8YTAz"
    b"hn7IHdSSD0lyLfqfOx3Y5FIPxnFUs3Jw9RUk7kLJerGJd/QF7eJxBTVIT38AAAAASUVORK5C"
    b"YII=")

# ----------------------------------------------------------------------
superscript = PyEmbeddedImage(
    b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAYFJ"
    b"REFUOI3VkTtPAlEQhUfW4INCxMpigcTEVhMbCxO2NDZgg6UUJpSIzZZS+AO201gYaa1MbEy2"
    b"EAosbCQxxFdUsKLjIffOndl1sTBYiEFjYzzVmWTmy8wZgH+voZ82ru0+RfWpkeOJUV/04lpY"
    b"J+ZMDgDA91NAwD9s3T9Q4vyqZS3Mjm//Ytl3pfZr5Y2D52qvHu4Z0zQLrusCEQEzAxGllFKH"
    b"iAiICLZtGzGzkhPoQvUWE725jxMcx7GYeV4pFSOicj6fr0opC1LKKjOnlrYqCZ8G0bvHtsHk"
    b"BOfWL6MAn0JMp9OGUuqMmaHT6WSVUgnbtg0AgJWdm4I+PRZzX7vwIl9bR5szwT4AAEAymbQc"
    b"x8kIIYCIJovFYnNQJn1fIKKcEAI8z4N2u537LtQ+gJTyWAiRRUTodruZSCRiDAJoPROPx4O6"
    b"ru8hYqFUKlmBQGDS7/cvNpvNVU3TTomoPhAQDodPETEopVShUKgupUw1Go0aM9eZeRkAyp7n"
    b"fQn5W70BAIHMJSEYEtgAAAAASUVORK5CYII=")
# ----------------------------------------------------------------------

# Custom pane bitmaps reference
#                      bitmap  button id       active  maximize
CUSTOM_PANE_BITMAPS = [(close, aui.AUI_BUTTON_CLOSE, True, False),
                       (close_inactive, aui.AUI_BUTTON_CLOSE, False, False),
                       (minimize, aui.AUI_BUTTON_MINIMIZE, True, False),
                       (minimize_inactive, aui.AUI_BUTTON_MINIMIZE, False, False),
                       (maximize, aui.AUI_BUTTON_MAXIMIZE_RESTORE, True, True),
                       (maximize_inactive, aui.AUI_BUTTON_MAXIMIZE_RESTORE, False, True),
                       (restore, aui.AUI_BUTTON_MAXIMIZE_RESTORE, True, False),
                       (restore_inactive, aui.AUI_BUTTON_MAXIMIZE_RESTORE, False, False)]

# ----------------------------------------------------------------------
# Custom buttons in tab area
#
CUSTOM_TAB_BUTTONS = {
    "Left": [(sort, aui.AUI_BUTTON_CUSTOM1), (superscript, aui.AUI_BUTTON_CUSTOM2)],
    "Right": [(fullscreen, aui.AUI_BUTTON_CUSTOM3), (remove, aui.AUI_BUTTON_CUSTOM4),
              (reload, aui.AUI_BUTTON_CUSTOM5)]
}

ArtIDs = [
    wx.ART_ADD_BOOKMARK, wx.ART_DEL_BOOKMARK, wx.ART_HELP_SIDE_PANEL, wx.ART_PRINT,
    wx.ART_HELP_SETTINGS, wx.ART_HELP_BOOK, wx.ART_HELP_FOLDER, wx.ART_HELP_PAGE,
    wx.ART_GO_BACK, wx.ART_GO_FORWARD, wx.ART_GO_UP, wx.ART_GO_DOWN, wx.ART_HELP,
    wx.ART_GO_TO_PARENT, wx.ART_GO_HOME, wx.ART_FILE_OPEN, wx.ART_MISSING_IMAGE,
    wx.ART_TIP, wx.ART_REPORT_VIEW, wx.ART_LIST_VIEW, wx.ART_NEW_DIR, wx.ART_HARDDISK,
    wx.ART_FLOPPY, wx.ART_CDROM, wx.ART_REMOVABLE, wx.ART_FOLDER, wx.ART_FOLDER_OPEN,
    wx.ART_GO_DIR_UP, wx.ART_EXECUTABLE_FILE, wx.ART_NORMAL_FILE, wx.ART_TICK_MARK,
    wx.ART_CROSS_MARK, wx.ART_ERROR, wx.ART_QUESTION, wx.ART_WARNING, wx.ART_INFORMATION
]


def rand_art_bitmap() -> wx.Bitmap:
    return wx.ArtProvider.GetBitmap(random.choice(ArtIDs), wx.ART_OTHER, (16, 16))
