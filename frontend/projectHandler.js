window.onload = async function convertPageElements() 
{   var createdOnObjectInitial = document.getElementById("createdOn")
    var createdOnObjectAfter = document.getElementById("createdOn-2")
    var modifiedOnObjectInitial = document.getElementById("modifiedOn")
    var modifiedOnOjbectAfter = document.getElementById("modifiedOn-2")
    var flipFrame1 = document.getElementById("flipFrame-1")
    var flipFrame2 = document.getElementById("flipFrame-2")
    var createdOn = (new Date(parseInt(createdOnObjectInitial.innerHTML) * 1000)).toLocaleString()
    var modifiedOn = (new Date(parseInt(modifiedOnObjectInitial.innerHTML) * 1000)).toLocaleString()
    createdOnObjectAfter.innerHTML = createdOn
    modifiedOnOjbectAfter.innerHTML = modifiedOn

    configFlipCard(createdOnObjectInitial, createdOnObjectAfter, flipFrame1)
    configFlipCard(modifiedOnObjectInitial, modifiedOnOjbectAfter, flipFrame2)
    await sleep(1 * 1000)
    document.getElementById('flipFrame-1').classList.add("flip-card-flip")
    await sleep(0.5* 1000)
    document.getElementById('flipFrame-2').classList.add("flip-card-flip")
}


function getMinimumTextDimensions(inputObject) 
{      
    text = document.createElement("span"); 
    document.body.appendChild(text);     
    text.style.font = inputObject.style.font
    text.style.fontSize = inputObject.style.fontSize;
    text.style.height = 'auto'; 
    text.style.width = 'auto'; 
    text.style.position = 'absolute'; 
    text.style.whiteSpace = 'no-wrap'; 
    text.innerHTML = inputObject.innerHTML
 
    width = Math.ceil(text.clientWidth); 
    height = Math.ceil(text.clientHeight);        
    document.body.removeChild(text); 
    return [width, height]
} 

function configFlipCard(front, back, coreDiv) 
{    
    [frontTextWidth, frontTextHeight] = getMinimumTextDimensions(front);
    [backTextWidth, backTextHeight] = getMinimumTextDimensions(back);    
    maxWidth = Math.max(frontTextWidth, backTextWidth);
    maxHeight = Math.max(frontTextHeight, backTextHeight);
    console.log(front.innerHTML)
    console.log(back.innerHTML)
    console.log(maxWidth)
    console.log(maxHeight)
    formattedWidth = maxWidth + "px"
    formattedHeight = maxHeight + "px"    
    front.style.height = formattedHeight;
    front.style.width = formattedWidth;
    coreDiv.style.height = formattedHeight;
    coreDiv.style.width = formattedWidth;
}


function sleep(ms)
{
    return new Promise(resolve => setTimeout(resolve, ms));
}

