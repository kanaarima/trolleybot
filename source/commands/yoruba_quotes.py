import random
import discord
from command import Command

yoruba_quotes = [
    "Top 60 and bullying a 4 digit is crazy; You must be very proud of yourself",
    "We needs to do something about sikkr",
    """okay great, murmur is still a peice of shit and I hope someone loses control of the steering wheel one day while he and his family are taking a walk outside
God I wish I could be the driver
not even joking rn""",
    "Your #1 is my #1 :niceone:",
    "https://cdn.discordapp.com/attachments/1225615897683820695/1226625293767278653/Screenshot_20240407_231024_Discord.jpg?ex=662572d3&is=6612fdd3&hm=ab3279363dd06872108328e23ef4d251bc21f62306df459fecde0d098ee00327&",
    "https://cdn.discordapp.com/attachments/1221708432663515196/1221952725856550972/SPOILER_Screenshot_1839.png?ex=661dada8&is=660b38a8&hm=8e857ce38b261aacdcbe30fca74f0f3cfeb0e12fbe92ad6e59cb5448ea588546&",
    "@Murmur got nun on me ness is targeting https://media.discordapp.net/attachments/1128767250938204220/1197848680351416320/IMG_8270.png?ex=66224604&is=660fd104&hm=d8e02cf8958acb1e6c4b4dea2c188e20e0c202f9e95b5465b1ef56843eefcfa1&=&format=webp&quality=lossless&width=306&height=663",
    "My clan has nothing to do with nazi symbolism but your clan is run by a cummunistic chinese man",
    """I have been fired 7 times.
I got cheated on.
I got banned from an housing agency.
Im banned from 4 supermarkets.
I have to pay for my mothers 12000. euro in debt because she fled the country.
I am broke as fuck and can't even buy the things I want in life.
I am addicted to weed and cannot stop it.

I charged back the money on paypal and you will recieve an invoice to pay the full 27 euro back to paypal and idk what paypal does to you when you owe them
This fucking game is the only thing that doesn't make me actually wanna kms and you now for some reason decided to ruin it even harder for me then it already was. I bought you a fucking tablet when im BROKE and you decide to snipe me on the maps that took me forever to get. I seriously cannot believe that this is happening. its now actually ruined. Fuck you""",
"""I have a life. Turned down potentially playing with Demon to go "touch grass" I have a job. pays well too @Yasubee 
@72.7% Meru again I never left #2. 
yes I fucking cried. Im human. I don't need to act like the scary black man 24/7. 

The reason im obsessed with farming #1 was purely just to spite @Remek cuz he made fun of me having 0. Thats why. 
I considered you guys my friends online or not doesn't matter to me.

And I expected all this from catso and verm but not the rest lmfao""",
"https://cdn.discordapp.com/attachments/1225615897683820695/1226628281869013082/Screenshot_20240407_232233_Discord.jpg?ex=6625759c&is=6613009c&hm=9877f5a3e0abd36c800a9c4131ec58988afd0b00a7b38633d9aa5607898aeabf&",
"https://cdn.discordapp.com/attachments/1225615897683820695/1226628861660237964/image.png?ex=66257626&is=66130126&hm=c29b13db5fd4d2e5c580cca041fcc9846ce8a1e8258c7dee318366a1121b523c&",
"https://cdn.discordapp.com/attachments/1225615897683820695/1226629444874010684/image0.jpg?ex=662576b1&is=661301b1&hm=ca7e2f4852535e607e78a5db21ff6f62f0820268938d2fd5f9b163d970c3ae3b&",
"""hello mr took my favorite pokemon song with pf mod from me while all I could do was watch in severe pain and agony ❤️
Wanna join my server? :p"""

]

class YorubaQuotesCommand(Command):
    def __init__(self) -> None:
        super().__init__("yorubaquote", "yoruba")
        
    async def run(self, message: discord.Message, args: list[str], parsed: dict[str, str]):
        await message.reply(f"{random.choice(yoruba_quotes)}")
        