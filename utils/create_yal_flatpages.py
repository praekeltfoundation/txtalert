# -*- coding: utf-8 -*-

from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from django.template.defaultfilters import slugify
from django.conf import settings

site = Site.objects.get(pk=settings.SITE_ID)



p736 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Help: at hand"""),
    title=u"""Help: at hand""",
    content=u"""
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/need-to-know-more-or-talk-to-someone/">Need to know more or talk to someone?</a></li>
<li><a href="/bookings/young-africa-live/want-to-get-tested-but-dont-know-where/">Want to get tested but don’t know where?</a></li>
<li><a href="/bookings/young-africa-live/need-help-after-a-rape-incident/">Need help after a rape incident?</a></li>
<li><a href="/bookings/young-africa-live/struggling-with-alcohol-drugs-or-substance-addiction/">Struggling with alcohol, drugs or substance addiction?</a></li>
<li><a href="/bookings/young-africa-live/helpful-aids-related-contact-numbers/">Helpful AIDS-related contact numbers</a></li>
        </ul>
    </p>
</div>""")
p736.sites.add(site)



p806 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Need to know more or talk to someone?"""),
    title=u"""Need to know more or talk to someone?""",
    content=u"""<div class="fp_content"><p>Try these nationwide helplines, free from a Telkom landline:<br />
    <br />
    <br />
    National AIDS Helpline<br />
    <br />
    <i>0800 012 322<br /></i><br />
    <br />
    Childline<br />
    <br />
    <i>0800 055 555<br /></i><br />
    <br />
    Stop Gender Violence Helpline<br />
    <br />
    <i>0800 150 150<br /></i><br />
    <br />
    Grants Helpline<br />
    <br />
    <i>0800 60 10 11<br /></i><br />
    <br />
    Lifeline<br />
    <br />
    <i>0860 322 322<br /></i></p></div>""")
p806.sites.add(site)



p804 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Want to get tested but don’t know where?"""),
    title=u"""Want to get tested but don’t know where?""",
    content=u"""<div class="fp_content"><p>There are testing sites all over South Africa. All government clinics and hospitals offer a free AIDS-testing facility. To find the nearest one call HIV 911 toll-free on 0860 448 911 (0860 HIV 911), or the National AIDS Helpline on <i>0800 012 322.</i><br />
    <br />
    <br />
    NEW START Testing facilities and counselling services:<br />
    <br />
    <br />
    <br />
    Johannesburg<br />
    <br />
    <i>011 484 5320</i><br />
    <br />
    <br />
    Durban<br />
    <br />
    <i>031 305 6942</i><br />
    <br />
    <br />
    Pietermaritzburg<br />
    <br />
    <i>033 342 3600<br /></i><br />
    <br />
    Cape Town<br />
    <br />
    <i>021 425 5843<br /></i><br />
    <br />
    Bloemfontein<br />
    <br />
    <i>051 430 9595<br /></i><br />
    <br />
    East London<br />
    <br />
    <i>043 743 3493</i><br />
    <br />
    <br />
    Umtata<br />
    <br />
    <i>047 532 4344</i><br />
    <br />
    <br />
    Nelspruit<br />
    <br />
    <i>013 754 6573</i><br />
    <br />
    <br />
    Polokwane<br />
    <br />
    <i>015 291 4843</i><br />
    <br />
    <br />
    Mafekeng<br />
    <br />
    <i>018 381 6849<br /></i></p></div>""")
p804.sites.add(site)



p803 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Need help after a rape incident?"""),
    title=u"""Need help after a rape incident?""",
    content=u"""<div class="fp_content"><p>If you were raped, you are entitled to ARV medicines to prevent you from getting AIDS. But you must start taking them within 72 hours of being raped. Contact these rape crisis centres to find out more:<br />
    <br />
    <br />
    <b>Johannesburg</b><br />
    <br />
    011 728 1347<br />
    <br />
    <br />
    <b>Pretoria </b><br />
    <br />
    012 342 2222<br />
    <br />
    <br />
    <b>Durban</b><br />
    <br />
    031 312 2323<br />
    <br />
    <br />
    <br />
    <b>Cape Town </b><br />
    <br />
    021 447 9762<br />
    <br />
    <br />
    <br />
    <b>Bloemfontein</b><br />
    <br />
    051 447 6678<br />
    <br />
    <br />
    <b>Kimberley</b><br />
    <br />
    053 831 1715<br />
    <br />
    <br />
    <br />
    <b>East London</b><br />
    <br />
    043 743 7266<br />
    <br />
    <br />
    <b>Port Elizabeth</b> <br />
    <br />
    041 484 3804<br />
    <br />
    <br />
    <b>Nelspruit  </b><br />
    <br />
    013 755 3606<br />
    <br />
    <br />
    <br />
    <b>Polokwane</b> <br />
    <br />
    015 297 7538<br />
    <br />
    <br />
    <b>Mafekeng</b> <br />
    <br />
    018 384 4870<br />
    <br /></p></div>""")
p803.sites.add(site)



p802 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Struggling with alcohol, drugs or substance addiction?"""),
    title=u"""Struggling with alcohol, drugs or substance addiction?""",
    content=u"""<div class="fp_content"><p>These people are here to help:<br />
    <br />
    Depression &amp; Anxiety group 24-hour Substance Abuse Helpline<br />
    <i>0800 121314<br /></i> <i>(or send an SMS to 32312)<br /></i><br />
    South African National Council on Alcoholism<br />
    &amp; Drug Dependence (SANCA)<br />
    <i>0864 SANCA<br /></i><br />
    Alcoholics Anonymous 0861 Help AA<br />
    <i>(0861 435 722)</i><br />
    <br />
    Lifeline: <br />
    <i>0861 322 322 <br /></i></p></div>""")
p802.sites.add(site)



p801 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Helpful AIDS-related contact numbers"""),
    title=u"""Helpful AIDS-related contact numbers""",
    content=u"""<div class="fp_content"><p>LoveLife Thetha Junction <br />
    <i>0800 121 900</i><br />
    <br />
    <br />
    LoveLife Parent Line<br />
    <br />
    <i>0800 121 100<br /></i><br />
    <br />
    Treatment Action Campaign (TAC)<br />
    <br />
    <i>021 422 1700<br /></i></p></div>""")
p801.sites.add(site)



p727 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""B the future"""),
    title=u"""B the future""",
    content=u"""<div class="fp_content"><p>Here is chapter one from the cellbook:<br />
    Basic facts about HIV and AIDS<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/11-what-is-hiv/">1.1 What is HIV?</a></li>
<li><a href="/bookings/young-africa-live/12-what-is-aids/">1.2 What is AIDS?</a></li>
<li><a href="/bookings/young-africa-live/13-how-do-i-get-infected/">1.3 How do I get infected?</a></li>
<li><a href="/bookings/young-africa-live/14-what-are-the-stages-of-the-disease/">1.4 What are the stages of the disease?</a></li>
<li><a href="/bookings/young-africa-live/15-what-increases-the-risk-of-becoming-infected/">1.5 What increases the risk of becoming infected?</a></li>
<li><a href="/bookings/young-africa-live/16-what-treatment-is-available/">1.6 What treatment is available?</a></li>
<li><a href="/bookings/young-africa-live/17-the-hiv-and-aids-epidemic-and-statistics/">1.7 The HIV and AIDS epidemic and statistics</a></li>
        </ul>
    </p>
</div>""")
p727.sites.add(site)



p783 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""1.1 What is HIV?"""),
    title=u"""1.1 What is HIV?""",
    content=u"""<div class="fp_content"><p>HIV stands for Human Immunodeficiency Virus. It is the virus that causes AIDS. It can only be transmitted from human to human. When the virus is in the human body it attacks the immune system.<br />
    <br />
    The immune system is very important - it protects the body by fighting off germs and infections. Normally, the body's immune system would be able to fight off infection.<br />
    <br />
    But HIV is able to infect key cells, called CD4 cells, which work to protect the body against infections. Over a long time HIV makes the immune system so weak that the body can no longer fight sickness. Once you have HIV in your body you are said to be HIV positive.<br />
    <br />
    The virus was originally identified in Paris in May 1983 by Luc Montagnier. It belongs to a group of viruses called retroviruses. Once cells become infected with HIV they stay infected for the rest of their lives.<br /></p></div>""")
p783.sites.add(site)



p787 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""1.2 What is AIDS?"""),
    title=u"""1.2 What is AIDS?""",
    content=u"""<div class="fp_content"><p>AIDS stands for Acquired Immuno Deficiency Syndrome.<br />
    A = Acquired<br />
    I = Immune<br />
    D = Deficiency<br />
    S = Syndrome<br />
    <br />
    Acquired: This means that you must do something to get AIDS. It cannot be passed through the air.<br />
    Immune: This is the body's defence system that fights germs and infections.<br />
    Deficiency: This relates to the lack of CD4 cells that help to fight infections.<br />
    Syndrome: This refers to a collection of different signs and symptoms that are all part of a certain medical condition.<br />
    <br />
    AIDS is the result of the damage caused by the HIV to the immune system. A damaged immune system is unable to protect the body against certain specific 'opportunistic' infections and tumours. They are called 'opportunistic' because they are caused by organisms that are normally controlled by the immune system but which 'take the opportunity' to cause disease if the immune system has been damaged.<br />
    <br />
    When you are HIV positive you might contract opportunistic infections such as Tuberculosis (TB), Pneumonia (PCP) and different forms of cancer (Kaposi's Sarcoma). Note: if you have TB, Pneumonia or cancer it does not mean that you are HIV positive. You still need to get an HIV test. Unlike most other diseases, different people with AIDS may experience different health problems, depending on which specific opportunistic infections they develop.  See 1.4 What are the stages of the disease?<br />
    <br />
    The National AIDS Helpline provides a confidential, anonymous 24-hour toll-free telephone counselling, information and referral service for those infected and affected by HIV and AIDS. The operator can give you a list of organisations providing support and care to HIV positive people and their families. Call 0800 012 322.</p></div>""")
p787.sites.add(site)



p788 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""1.3 How do I get infected?"""),
    title=u"""1.3 How do I get infected?""",
    content=u"""<div class="fp_content"><p>HIV can only be transmitted in:<br />
    <br />
     Blood (including menstrual blood)<br />
     Semen<br />
     Vaginal fluids<br />
     Breast milk<br />
    <br />
    HIV can only be passed to another person if these fluids get into the other person's body. The level of the virus in other bodily fluids such as saliva is far too low to be infectious. High-level laboratory techniques can detect the virus in other body fluids of HIV positive people but these are not infectious.<br />
    <br />
    HIV can be transmitted through having unprotected sex<br />
    <br />
    * Unprotected vaginal or anal intercourse with an HIV positive person puts you at risk of becoming infected. In South Africa, this is the most common way that HIV is spread.<br />
    * Anal intercourse is the most risky sexual behavior as it often leads to small tears through which the virus will pass easily.<br />
    * Oral sex may be unsafe if there are small cuts in the mouth and/or gum.<br />
    * The risk of HIV transmission through unprotected sex applies to all couples, whether you are in a heterosexual or same sex relationship.<br />
    * In heterosexual relationships, women are more at risk of infection by an HIV positive male partner than men are of being infected by an HIV positive female partner.<br />
    * In same sex relationships between men, anal sex is the most common form of transmission of HIV.<br />
    <br />
    HIV can be transmitted from a mother to her baby<br />
    <br />
    Mothers living with HIV run the risk of transmitting HIV to their infants during pregnancy, labour, delivery or breastfeeding.<br />
    This is called Mother-to-Child Transmission (MTCT).<br />
    <br />
    <br />
    HIV can be transmitted through intravenous drug use<br />
    <br />
    * Injecting drug users (IDUs) are at risk of becoming infected with HIV through the sharing of contaminated needles and/or syringes.<br />
    * When a person shoots drugs, a small amount of blood remains inside the needle and/or syringe. If the person is HIV positive, when others use the same needle, they inject the infected blood into their bloodstream.<br />
    <br />
    HIV can be transmitted through contact with contaminated blood and blood products<br />
    <br />
    * HIV can be transmitted through infected blood and blood products.<br />
    * In the past, before screening was introduced, HIV was transmitted through blood transfusions or from infected blood products.<br />
     These days, all donated blood used in hospitals is screened to prevent this.<br />
    * Universal Precautions are a set of precautions designed to prevent transmission of HIV when providing first aid or health care.<br />
    It is important to practise Universal Precautions - protect yourself by always wearing gloves when you work with blood or open wounds even when you know the person's HIV status.<br />
    <br />
    HIV can be transmitted through occupational exposure<br />
    <br />
    * HIV transmission can happen through accidents in the workplace.<br />
    * Healthcare workers or those who care for HIV positive people may come into contact accidentally with contaminated body fluids or may mistakenly prick themselves with a needle. However many research studies have proven that the virus is too weak to survive for long periods outside of the body so this risk is small.<br />
    <br />
    You can't get HIV from:<br />
    <br />
    * Hugging<br />
    * Casual kissing<br />
    * Saliva, tears or sweat<br />
    * Touching<br />
    * Sharing a home<br />
    * Sharing utensils such as forks and spoons<br />
    * Touching a toilet seat, telephone or doorknob<br />
    * Eating or playing together<br />
    * Mosquitoes or other insects<br /></p></div>""")
p788.sites.add(site)



p785 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""1.4 What are the stages of the disease?"""),
    title=u"""1.4 What are the stages of the disease?""",
    content=u"""<div class="fp_content"><p>After you have been infected with HIV, the virus follows four stages of infection. During the first two stages you normally do not see any symptoms of the disease. AIDS-related symptoms usually only appear during the final two stages.</p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/stage-1-acute-infection/">Stage 1: Acute infection</a></li>
<li><a href="/bookings/young-africa-live/stage-2-asymptomatic-hiv-infection/">Stage 2: Asymptomatic HIV infection</a></li>
<li><a href="/bookings/young-africa-live/stage-3-symptomatic-hiv-infection/">Stage 3: Symptomatic HIV infection</a></li>
<li><a href="/bookings/young-africa-live/stage-4-acquired-immuno-deficiency-syndrome-aids/">Stage 4: Acquired Immuno-deficiency Syndrome (AIDS)</a></li>
        </ul>
    </p>
</div>""")
p785.sites.add(site)



p791 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Stage 1: Acute infection"""),
    title=u"""Stage 1: Acute infection""",
    content=u"""<div class="fp_content"><p>* This is when you first come into contact with HIV. This stage - sometimes called the 'window period' - lasts approximately 6-9 weeks. Most people do not notice that they have been infected.<br />
    <br />
    * Some people have a short illness soon after they become infected such as a sore throat, ulcers in the mouth or genitals, a fever or a rash, diarrhea, severe headaches or, rarely, a more severe illness such as meningitis as a result of severe immune suppression.<br />
    <br />
    * During this stage, the result of an HIV test will show that you do not have HIV because the test is looking for antibodies for HIV and as yet your body has not developed any. Antibodies are a type of protein produced by the immune system when it detects a foreign substance that may be a threat to the body. So you should go for another test a few months later.<br />
    <br />
    * Remember that the symptoms described above could also be caused by other infections such as flu, glandular fever and tonsillitis.</p></div>""")
p791.sites.add(site)



p792 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Stage 2: Asymptomatic HIV infection"""),
    title=u"""Stage 2: Asymptomatic HIV infection""",
    content=u"""<div class="fp_content"><p>* This is called the asymptomatic stage as you will have no signs or symptoms of HIV and will probably feel completely healthy.<br />
    <br />
    * Because you may feel and look fine on the outside, two tests are extremely important as they will help you to understand how strong your immune system actually is. Signs of immune damage can be detected by two laboratory tests:<br />
    - CD4 cell count<br />
    CD4 cells are cells in your body attached to the immune system. As HIV attacks the immune system, so the number of CD4 cells drop. Changes in CD4 cell count are helpful in showing whether or not HIV is damaging the immune system. A normal CD4 cell count in a person without HIV varies between 400 and 1600 cells per mm3. Immediately after a person becomes infected with HIV the CD4 cell count is likely to fall to a level several hundred cells below normal.<br />
    - Viral load test<br />
    This test detects the amount of HIV in your blood. The amount of virus is counted in the form of 'copies' per milliliter (ml) of blood: 10,000 copies per ml is low, and more than 100,000 copies per ml is high. Your viral load can go up briefly if you have an infection. Single viral load results don't matter as much as the trend in your viral load results.<br />
    <br />
    * The HI virus is always active in your body once you are infected. HIV actively increases during the asymptomatic period, mainly in the lymph nodes and lymphoid tissue, which are a perfect environment for the infection of new CD4 cells.<br />
    <br />
    * It is important to note that while you may feel fine, you are still able to infect others with the virus through unprotected sex and exposure to blood. The duration of this stage varies widely from one person to another. Some people decline rapidly in 2 years but 10 to 15% of people may show no signs of progression for 10 or more years.</p></div>""")
p792.sites.add(site)



p793 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Stage 3: Symptomatic HIV infection"""),
    title=u"""Stage 3: Symptomatic HIV infection""",
    content=u"""<div class="fp_content"><p>* Now the immune system is fighting the virus while it infects more and more cells. For many years, the immune system can control the virus, but eventually the immune system starts losing the battle. The virus begins to destroy the CD4 cell population.<br />
    <br />
    * As the CD4 counts continue to drop, signs and symptoms more specific to HIV disease may arise, such as:<br />
    - Weight loss<br />
    - Diarrhea<br />
    - Oral thrush and ulcers<br />
    - Shingles (a painful skin rash)<br />
    - Meningitis or peripheral neuropathy</p></div>""")
p793.sites.add(site)



p794 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Stage 4: Acquired Immuno-deficiency Syndrome (AIDS)"""),
    title=u"""Stage 4: Acquired Immuno-deficiency Syndrome (AIDS)""",
    content=u"""<div class="fp_content"><p>* Because there is no single way for doctors to make an AIDS diagnosis they look at a number of different factors, which may indicate that the HIV infection has progressed to AIDS.<br />
    Note: this is different from testing for HIV - See 3. How do I know my HIV status?<br />
    <br />
    * You have AIDS when you are HIV positive, your CD4 is below 200 and you suffer from one or more of these secondary infections:<br />
    - Tuberculosis (TB)<br />
    - Types of cancers such as Kaposi's Sarcoma, cervical cancer and Lymphoma (enlarged lymph nodes, liver or spleen)<br />
    - Pneumonia (PCP)<br />
    - Meningitis/encephalitis<br />
    - HIV Dementia<br />
    Many of these opportunistic (secondary) infections can be treated at any stage of HIV disease.</p></div>""")
p794.sites.add(site)



p786 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""1.5 What increases the risk of becoming infected?"""),
    title=u"""1.5 What increases the risk of becoming infected?""",
    content=u"""<div class="fp_content"><p>Sexually Transmitted Infections (STIs)<br />
    <br />
    * STIs are infections that pass from one person to another, mainly through sexual intercourse. There are lots of different types of STIs: syphilis, gonorrhea, herpes, HIV, genital warts or crabs (lice). HIV is the only type of STI that causes AIDS. It is the most serious STI - the others are easily treatable and curable.<br />
    <br />
    * Getting an STI (besides HIV) increases the chance of HIV infection. The sores on your penis or vagina help the HIV enter your body through the broken skin, which cannot act as a barrier to HIV. These sores can also start to bleed during sex and this will make it easier for the HIV to enter your body. A discharge also makes it easier to get HIV.<br />
    <br />
    * An untreated STI can make someone who is HIV positive more infectious. For example, when untreated, gonorrhea can make a person with HIV more infectious as gonorrhea increases the number of HIV-infected cells in the genital area and in the mucous membranes of the mouth and throat.<br />
    <br />
    * If you have an STI, it is important to use a condom when having sex to prevent it spreading further. Most STIs are very easy and cheap to treat. This can be done at a clinic or by your doctor, free of charge or for a small fee.<br />
    <br />
    Drug and alcohol abuse<br />
    <br />
    * HIV can be spread because you make bad judgment calls when you are under the influence of drugs. For example, when you are high you do not think clearly and have sex without a condom.<br />
    * Alcohol doesn't cause HIV infection. Alcohol reduces your ability to think clearly and you become more likely to make impulsive decisions and have unprotected sex.<br />
    <br />
    * If you are living with HIV, drug and alcohol abuse weakens the immune system. If you are HIV negative, a person with a poor immune system is more likely to become infected with HIV if he/she has unprotected sex.</p></div>""")
p786.sites.add(site)



p789 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""1.6 What treatment is available?"""),
    title=u"""1.6 What treatment is available?""",
    content=u"""<div class="fp_content"><p>* Many years may pass between becoming HIV positive and actually developing AIDS.<br />
    <br />
    * AIDS can be treated. As HIV progresses and the immune system weakens, you may get opportunistic infections (OIs). All clinics offer treatments for opportunistic infections.<br />
    <br />
    * Antiretroviral (ARV) therapy can also help you to live a longer, healthier life. ARVs are a lifelong treatment but not a cure for AIDS. Most people with HIV only need to take ARVs after many years.<br />
    <br />
    * In the meantime you should ask for regular CD4 and viral load tests to monitor the progression of HIV in your body. This will tell you how healthy your immune system is and the level of HIV in your body.<br />
    <br />
    * Guidelines have been developed in South Africa to help doctors, nurses, healthworkers and you decide if and when to start with antiretroviral treatment, usually if your CD4 count is near or below 200. There are many different HIV drugs and the Guidelines recommend what ARV combinations to start with.<br /></p></div>""")
p789.sites.add(site)



p790 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""1.7 The HIV and AIDS epidemic and statistics"""),
    title=u"""1.7 The HIV and AIDS epidemic and statistics""",
    content=u"""
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/why-is-hiv-and-aids-a-global-epidemic/">Why is HIV and AIDS a 'global' epidemic?</a></li>
<li><a href="/bookings/young-africa-live/the-south-african-epidemic/">The South African epidemic</a></li>
<li><a href="/bookings/young-africa-live/why-is-the-aids-epidemic-so-big-in-south-africa/">Why is the AIDS epidemic so big in South Africa?</a></li>
<li><a href="/bookings/young-africa-live/how-can-south-africa-achieve-a-summer-for-all-people/">How can South Africa achieve a 'Summer for All People'?</a></li>
        </ul>
    </p>
</div>""")
p790.sites.add(site)



p795 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Why is HIV and AIDS a 'global' epidemic?"""),
    title=u"""Why is HIV and AIDS a 'global' epidemic?""",
    content=u"""<div class="fp_content"><p>* HIV's rapid spread through different parts of the world has led to it being described as a 'global' epidemic. Although the global HIV and AIDS epidemic is not growing anymore, it remains at an unacceptably high level.<br />
    <br />
    * The Joint United Nations Programme on HIV and AIDS (UNAIDS) estimates that, in 2007, there were 33 million people living with HIV across the world. [1]<br />
    <br />
    * Sub-Saharan Africa (African countries south of the Saharan dessert), has more HIV positive people and AIDS deaths than any other part of the world: 67% of all HIV positive people and 72% of all AIDS deaths were in Sub-Saharan Africa in 2007. [2]<br />
    <br />
    * Globally there are around 2 million HIV positive children (younger than 15 years), of whom 90% live in Sub-Saharan Africa.<br />
    <br />
    * UNAIDS states that the percentage of young pregnant women (15-24 year old), who are HIV positive, has reduced since 2000-2001.<br />
    <br />
    * There are still around 2.7 million new infections every year.</p></div>""")
p795.sites.add(site)



p798 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""The South African epidemic"""),
    title=u"""The South African epidemic""",
    content=u"""<div class="fp_content"><p>* South Africa is experiencing the largest HIV and AIDS epidemic in the world - an estimated 5.7 million South Africans are HIV positive in 2009.<br />
    <br />
    * Around 20% of the adults in South Africa (ages 20-64) are HIV positive, as are around 29% of the women visiting antenatal clinics. This means that one in every five adults in South Africa is HIV positive.<br />
    <br />
    * In 2009, it is estimated that there are still around 1400 new HIV infections and around 1000 AIDS deaths every day.<br />
    <br />
    * Around 2.9 million South African have died from AIDS-related illnesses since the start of the epidemic. [3]<br />
    <br />
    * There is currently no cure for HIV. As long as there are more new infections than deaths, the total number of HIV positive people will continue to grow. It is interesting to note that if there are more deaths than new infections, the total number of HIV positive people will reduce. A smaller epidemic might not mean that we are 'winning the battle against new infections', it might mean that we are 'losing the battle against preventing AIDS deaths'.<br />
    <br />
    * South Africa has made progress in the treatment of AIDS sick patients. Around 60% of those in need of antiretroviral treatment were receiving treatment through public and private healthcare facilities by the end of 2008 [4]. More and more pregnant women receive antiretroviral treatment to prevent passing on the virus from mother to child.<br />
    <br />
    * Different provinces in South Africa experience different levels of HIV infections and AIDS related deaths:<br />
    - Kwazulu-Natal is experiencing the largest HIV epidemic in the country. Nearly 1.6 million people and almost a third of the adult population are HIV positive. Take-up on treatment has been slow.<br />
    - Gauteng has the second largest HIV epidemic with around 1.4 million HIV positive people and one in every five adults. Take-up on treatment is growing rapidly.<br />
    - The Eastern Cape epidemic is one of the fastest growing in the country with around 730 000 HIV positive people and one in every five adults. Take-up on treatment has also been extremely slow.<br />
    - Other provinces with big mature epidemics (epidemics with stable numbers of new infections and deaths) are the North West (500 000 HIV positive), Mpumalanga (450 000 HIV positive) and the Free State (400 000).<br />
    - The epidemic in Limpopo is also relatively big (430 000 HIV positive) and still growing.<br />
    - The Western Cape has the smallest HIV prevalence rate (6% of the total population or 300 000 people estimated to be HIV positive). Although the take-up on treatment is the highest, the province is still experiencing a growing epidemic.<br />
    - The Northern Cape epidemic is the smallest with around 67 000 people HIV positive. The epidemic in the province is also still growing. [5]</p></div>""")
p798.sites.add(site)



p799 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Why is the AIDS epidemic so big in South Africa?"""),
    title=u"""Why is the AIDS epidemic so big in South Africa?""",
    content=u"""<div class="fp_content"><p>There are several reasons for the HIV and AIDS epidemic killing South Africans:<br />
    <br />
    * There is a lot of risky sexual behaviour in South Africa:<br />
    <br />
    - People don't use a condom every time they have sex.<br />
    - Many start having sex when they are very young which increases their chance of becoming infected.<br />
    - When HIV positive people have sex with older or younger partners the virus moves from generation to generation<br />
    - HIV positive people who don't know their status don't know they are infecting others.<br />
    - People change sexual partners often or have more than one sexual partner.<br />
    - Some people exchange sex for money or possessions.<br />
    <br />
    * The South African environment makes it easier to get infected through:<br />
    <br />
    - More and more South Africans move to cities where they have several sexual partners making it easier for the virus to spread.<br />
    - Poorer South African women may not be able to protect themselves from getting infected due to their low status in the community.<br />
    - It's easy for South Africans to travel from place to place so the disease is spread across different areas.<br />
    - Sexual violence is very high in South Africa - HIV infection might happen as a result of rape or sexual abuse.<br />
    - Some South African women believe men should be knowledgeable in sexual matters so they don't find out about AIDS and HIV. Others might feel pressurised to have children with a partner without knowing their HIV status.<br />
    - Some men might believe it is their right to have more than one partner without protecting themselves against infection or infecting others.</p></div>""")
p799.sites.add(site)



p800 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""How can South Africa achieve a 'Summer for All People'?"""),
    title=u"""How can South Africa achieve a 'Summer for All People'?""",
    content=u"""<div class="fp_content"><p>The Metropolitan Live the Future scenarios are four different possible situations that may unfold in South Africa until 2025, depending on how we respond to HIV and AIDS. The best case scenario is called the Summer for All People.<br />
    Under the Summer scenario, the HIV and AIDS epidemic drops dramatically and all South Africans enjoy life under the African sun. It is the only scenario that succeeds in bringing adult HIV prevalence rates down from 20% to 7% through economic growth, working together and a strong focus on prevention. It predicts that South Africans will respond successfully to the epidemic through:<br />
    <br />
    * Individual behaviour change<br />
    - Everyone focuses on prevention of HIV infection.<br />
    - Everyone takes personal responsibility for their sexual behaviour and health.<br />
    - People change their sexual behaviour.<br />
    - South Africans test regularly for HIV so that most people are aware of their HIV status by 2010.<br />
    - All South Africans use condoms consistently and correctly.<br />
    - South Africans remain faithful to one sexual partner<br />
    <br />
    * Collaboration: Strong leaders in government, the community and business standing together.<br />
    <br />
    * Partnerships: The private sector (business) and the public sector (NGOs and government) form partnerships to tackle specific problems.<br />
    <br />
    YOU DO NOT NEED TO BE ANOTHER HIV STATISTIC! BECOME PART OF SUMMER FOR ALL PEOPLE - KNOW AND/OR MANAGE YOUR HIV STATUS!<br />
    <br />
    Read more about the Live the Future model on:<br />
    www.livethefuture.co.za<br />
    <br />
    e-mail Metropolitan:<br />
    livethefuture@metropolitan.co.za<br />
    <br />
    References: [1] UNAIDS, 2008, Report on the Global HIV/AIDS epidemic 2008: Executive Summary [2] UNAIDS, 2008, Report on the Global HIV/AIDS epidemic 2008: Executive Summary [3] Actuarial Society of South Africa, 2006, ASSA2003 (Full) AIDS and Demographic model (projected by Nathea Nicolay) [4] Metropolitan AIDS Risk Consulting, 2009. [5] Nathea Nicolay, Metropolitan, Oct 2008, Summary of provincial HIV and AIDS Statistics for South Africa.<br /></p></div>""")
p800.sites.add(site)



p724 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""HIV: the facts"""),
    title=u"""HIV: the facts""",
    content=u"""
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/hiv-basics/">HIV Basics</a></li>
<li><a href="/bookings/young-africa-live/dont-get-infected/">Don’t get infected</a></li>
<li><a href="/bookings/young-africa-live/get-tested/">Get tested</a></li>
<li><a href="/bookings/young-africa-live/just-diagnosed/">Just diagnosed?</a></li>
<li><a href="/bookings/young-africa-live/staying-healthy-if-youre-hiv/">Staying healthy if you’re HIV+</a></li>
<li><a href="/bookings/young-africa-live/sex-if-youre-hiv/">Sex if you’re HIV+</a></li>
<li><a href="/bookings/young-africa-live/treatment/">Treatment</a></li>
<li><a href="/bookings/young-africa-live/opportunistic-infections-tb/">Opportunistic infections (TB)</a></li>
<li><a href="/bookings/young-africa-live/hiv-and-pregnancy/">HIV and pregnancy</a></li>
<li><a href="/bookings/young-africa-live/hiv-and-your-rights/">HIV and your rights</a></li>
        </ul>
    </p>
</div>""")
p724.sites.add(site)



p728 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""HIV Basics"""),
    title=u"""HIV Basics""",
    content=u"""<div class="fp_content"><p>HIV is a serious problem in South Africa. 1 in every 5 of us has it. HIV affects everyone, no matter what race, sex or age you are. So you have to take it seriously.<br />
    <br />
    People with HIV get sick easier and will die if they don’t get treated. Luckily there are drugs to treat HIV these days – they’re called ARVs. That’s why it’s important to know your HIV status.<br />
    <br />
    Want to know more about HIV and AIDS? Find out:</p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/how-you-get-infected/">How you get infected</a></li>
<li><a href="/bookings/young-africa-live/how-you-dont/">How you don’t</a></li>
        </ul>
    </p>
</div>""")
p728.sites.add(site)



p729 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""How you get infected"""),
    title=u"""How you get infected""",
    content=u"""<div class="fp_content"><p>HIV spreads through bodily fluids: blood, semen (sperm), vaginal fluid and breast milk. If those fluids from an HIV+ person get into your body, you can get HIV.</p></div>""")
p729.sites.add(site)



p730 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""How you don’t"""),
    title=u"""How you don’t""",
    content=u"""<div class="fp_content"><p>You CAN’T get infected from:<br />
        Kissing<br />
        Sharing plates and cutlery<br />
        Sneezing<br />
        Tears<br />
        Mosquitoes.<br />
    <br />
    The best plan with HIV is not to get infected in the first place. This means not sharing blood, semen,  vaginal fluids or breast milk. To be safe, assume that your sex partners are HIV+. After all, you can’t tell by how they look. Don’t get infected. Return to the Main Menu to find out how.<br /></p></div>""")
p730.sites.add(site)



p731 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Don’t get infected"""),
    title=u"""Don’t get infected""",
    content=u"""<div class="fp_content"><p>Don’t share blood, semen or vaginal fluids with anybody else. Only you can protect yourself. Always assume that your sex partners are HIV+ because even if they say they aren’t, they could be lying just to have sex with you. Even then, some people can get HIV from their steady partners who were unfaithful ‘just once’. Only you can look after you. Read more on how to keep yourself safe:<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/safe-sex/">Safe sex</a></li>
<li><a href="/bookings/young-africa-live/alcohol-and-drugs/">Alcohol and drugs</a></li>
<li><a href="/bookings/young-africa-live/rape-and-sexual-assault/">Rape and sexual assault</a></li>
<li><a href="/bookings/young-africa-live/mother-to-baby/">Mother-to-baby</a></li>
        </ul>
    </p>
</div>""")
p731.sites.add(site)



p771 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Safe sex"""),
    title=u"""Safe sex""",
    content=u"""<div class="fp_content"><p>Unprotected, penetrative sex (sex without a condom where the penis enters the vagina or anus) is the main way you get HIV. This is because you exchange bodily fluids (semen, vaginal fluids, sometimes even blood). Read more on how safe sex can prevent HIV:<br />
    <br />
    <br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/should-i-be-having-sex/">Should I be having sex?</a></li>
<li><a href="/bookings/young-africa-live/being-faithful/">Being faithful</a></li>
<li><a href="/bookings/young-africa-live/male-condom/">Male condom</a></li>
<li><a href="/bookings/young-africa-live/female-condom/">Female condom</a></li>
<li><a href="/bookings/young-africa-live/fun-safe-stuff/">Fun safe stuff</a></li>
<li><a href="/bookings/young-africa-live/myths/">Myths</a></li>
<li><a href="/bookings/young-africa-live/sex-with-many-partners/">Sex with many partners</a></li>
        </ul>
    </p>
</div>""")
p771.sites.add(site)



p782 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Should I be having sex?"""),
    title=u"""Should I be having sex?""",
    content=u"""<div class="fp_content"><p>Not having sex is an almost 100% way of avoiding HIV! Maybe you feel like your body is ready to have sex, but you might not be ready to deal with the responsibilities like potential disease, pregnancy and complications in relationships. You can show someone you love them in ways other than sex. And if they love you, they should respect your decision!<br /></p></div>""")
p782.sites.add(site)



p781 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Being faithful"""),
    title=u"""Being faithful""",
    content=u"""<div class="fp_content"><p>A relationship where both partners are HIV-negative and 100% faithful to each other is safe.<br />
    <br />
    <br />
    When you want to have sex for the first time with your partner, get tested for HIV. Even if you’re both negative, use condoms for the next 3 months. (You could have HIV but it doesn’t show on the test). Then test again. Only if that test is negative can you have sex without a condom (but remember infections and pregnancy!).<br />
    <br />
    <br />
    If either of you has sex with someone else, even once, you have to repeat this process. You both have to be honest and mature – slipping up just once puts you both at risk.<br />
    <br />
    <br /></p></div>""")
p781.sites.add(site)



p780 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Male condom"""),
    title=u"""Male condom""",
    content=u"""<div class="fp_content"><p>The male condom protects against HIV as it acts as a barrier – it stops the penis and the vagina or anus from touching each other, and stops fluids being exchanged. You have to use condoms EVERY time you have sex. Get them free at government clinics.<br /></p></div>""")
p780.sites.add(site)



p779 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Female condom"""),
    title=u"""Female condom""",
    content=u"""<div class="fp_content"><p>This condom goes inside the woman’s vagina. It works the same as the male condom as it stops the penis and vagina touching each other, and stops fluids being exchanged. It’s harder to get hold of than the male condom. Some women prefer to use them because you can put them in long before you have sex.<br /></p></div>""")
p779.sites.add(site)



p776 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Fun safe stuff"""),
    title=u"""Fun safe stuff""",
    content=u"""<div class="fp_content"><p>Fantasy, masturbation or hand jobs (where you keep your fluids to yourself), sexy talk, and non-sexual massage are safe. These activities avoid contact with blood or sexual fluids, so there is no risk of HIV.<br />
    <br />
    <br />
    Oral sex<br />
    You can get HIV from oral sex, though the risk is small. Remember that you can also get other sexually transmitted infections (eg drop, herpes) from oral sex. To be safe, read about:<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/oral-sex-on-a-man/">Oral sex on a man</a></li>
<li><a href="/bookings/young-africa-live/oral-sex-on-a-woman/">Oral sex on a woman</a></li>
        </ul>
    </p>
</div>""")
p776.sites.add(site)



p778 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Oral sex on a man"""),
    title=u"""Oral sex on a man""",
    content=u"""<div class="fp_content"><p>Don’t have oral sex when you have a throat infection or bleeding gums.<br />
    For safe oral sex you should: avoid getting semen in your mouth; use a condom; have oral sex with fewer men; look after your oral hygiene.<br />
    <br /></p></div>""")
p778.sites.add(site)



p777 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Oral sex on a woman"""),
    title=u"""Oral sex on a woman""",
    content=u"""<div class="fp_content"><p>Don’t give a woman oral sex when she is having her period.<br />
    For safe oral sex you should: use a barrier such as cling-film, a dental dam, a Femidom or a sheet cut from a condom; have oral sex with fewer women; look after your oral hygiene.<br /></p></div>""")
p777.sites.add(site)



p775 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Myths"""),
    title=u"""Myths""",
    content=u"""<div class="fp_content"><p>Some men think that they can’t transmit HIV if they pull their penis out before they reach orgasm. This isn’t true, because HIV can be in the fluid that comes out of the penis before orgasm.<br />
    <br />
    <br />
    Don’t think that 2 condoms are better than 1. Actually, 2 male condoms or 1 male + 1 female is not a good combo, because friction means that the chances of them breaking are higher.<br />
    <br />
    <br />
    If 2 people are HIV+ it does not mean they should not practise safe sex. Actually, they can re-infect each other with different types of HIV. Also they can pass on other STI’s like gonorrhoea (drop), herpes etc.<br /></p></div>""")
p775.sites.add(site)



p772 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Sex with many partners"""),
    title=u"""Sex with many partners""",
    content=u"""<div class="fp_content"><p>Having many sexual partners at the same time really increases your chances of getting HIV.<br />
    It’s like a computer virus. When one computer gets it, it spreads really fast on a network. HIV is just like that, especially because you are most infectious when you’ve just got it (and don’t even know!). Remember that unprotected sex means you are having sex with all current and previous sexual partners of the person you are in bed with.<br />
    <br />
    <br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/but-i-want-good-sex/">‘But I want good sex’</a></li>
<li><a href="/bookings/young-africa-live/but-men-need-it/">'But men need it’</a></li>
        </ul>
    </p>
</div>""")
p772.sites.add(site)



p774 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""‘But I want good sex’"""),
    title=u"""‘But I want good sex’""",
    content=u"""<div class="fp_content"><p>You can have it! Communicate with your partner about your needs and what turns you on. That way you build your relationship and a good sex life. Ya, it’s work. But the hard work of living with HIV is much more than putting effort into your sex life.<br /></p></div>""")
p774.sites.add(site)



p773 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""'But men need it’"""),
    title=u"""'But men need it’""",
    content=u"""<div class="fp_content"><p>Some say ‘men can’t control themselves and need lots of partners’. Rubbish! Men are not animals and many men are happy with 1 partner. It’s a matter of choice – you choose how you want to live your life.<br /></p></div>""")
p773.sites.add(site)



p770 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Alcohol and drugs"""),
    title=u"""Alcohol and drugs""",
    content=u"""<div class="fp_content"><p>Drugs are risky because people sometimes share needles or syringes for injecting drugs and if you’re sharing with someone HIV+, you can easily get HIV.<br />
    <br />
    <br />
    Also drugs (and alcohol) cloud your judgment and may lead you to make unsafe choices. When you’re high, you’re unlikely to think about using a condom.<br /></p></div>""")
p770.sites.add(site)



p769 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Rape and sexual assault"""),
    title=u"""Rape and sexual assault""",
    content=u"""<div class="fp_content"><p>Someone who has been raped or sexually assaulted can take drugs called PEP (post-exposure prophylaxis) to stop them getting HIV. The person who has been raped should be offered the option of using the free drugs after counselling at a government hospital. The drugs must be started within 72 hours.<br /></p></div>""")
p769.sites.add(site)



p768 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Mother-to-baby"""),
    title=u"""Mother-to-baby""",
    content=u"""<div class="fp_content"><p>A pregnant woman can pass HIV to her baby before, during or after birth. If she is HIV+, she can access PMTCT services where she is given drugs before and during the birth, and the newborn is given drugs straight after. This greatly reduces the chances of the baby being HIV+.<br /></p></div>""")
p768.sites.add(site)



p763 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Get tested"""),
    title=u"""Get tested""",
    content=u"""<div class="fp_content"><p>Testing is voluntary (you can’t be forced to test), and confidential (health workers can’t tell anyone your results except you). If you’ve had unprotected sex or you’ve been in contact with someone else’s blood, get tested. These days HIV is <i>not</i> a death sentence – so rather know your status and do something about it than stay ignorant and hope for the best.<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/the-testing-process/">The testing process</a></li>
<li><a href="/bookings/young-africa-live/types-of-tests/">Types of tests</a></li>
<li><a href="/bookings/young-africa-live/where-can-i-test/">Where can I test?</a></li>
<li><a href="/bookings/young-africa-live/what-if-im-positive/">What if I’m positive?</a></li>
        </ul>
    </p>
</div>""")
p763.sites.add(site)



p767 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""The testing process"""),
    title=u"""The testing process""",
    content=u"""<div class="fp_content"><p>Voluntary counselling and testing (VCT) services are offered at health facilities around the country. There test has 3 parts:<br />
    pre-test counselling, where you are prepared for the test and what a positive result may mean;<br />
    the HIV test itself;<br />
    and post-test counselling, where you’re given your result.<br />
    If your test is positive, you will receive immediate emotional support and information on where to find ongoing help.<br />
    <br />
    <br /></p></div>""")
p767.sites.add(site)



p766 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Types of tests"""),
    title=u"""Types of tests""",
    content=u"""<div class="fp_content"><p>Mostly the ‘rapid test’ is used. It tests blood or saliva. The results are very quick. But sometimes, samples are sent to a lab for testing so you have to go back to get your results.<br />
    <br />
    <br /></p></div>""")
p766.sites.add(site)



p765 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Where can I test?"""),
    title=u"""Where can I test?""",
    content=u"""<div class="fp_content"><p>There are testing sites all over South Africa. For the nearest one call the National AIDS Helpline 0800 0123 22, or SMS your postcode and HIV to 31771.<br /></p></div>""")
p765.sites.add(site)



p764 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""What if I’m positive?"""),
    title=u"""What if I’m positive?""",
    content=u"""<div class="fp_content"><p>If you tested positive, it means you are infected with HIV. You may feel shock, anger, fear or guilt. These strong feelings are normal. It could take time for you to accept your HIV+ status.<br />
    <br />
    <br />
    Try to remember that HIV is not a death sentence – with a healthy lifestyle and ARVs (medication for HIV) when you need them, you can live a long life. When you feel ready, talk to someone you trust who can give you support (a family member, friend, counsellor, doctor or traditional healer). You can also call the National AIDS Helpline on 0800 012 322 – they are there to help you.<br /></p></div>""")
p764.sites.add(site)



p754 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Just diagnosed?"""),
    title=u"""Just diagnosed?""",
    content=u"""<div class="fp_content"><p>Learning that you have HIV is scary – but it’s not a death sentence. If you live healthily, eat well and take medication when necessary, you can live a long life. Here are 7 steps to help you cope. (You don’t have to follow them in this order!)<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/take-control/">Take control</a></li>
<li><a href="/bookings/young-africa-live/go-back-to-the-clinic/">Go back to the clinic</a></li>
<li><a href="/bookings/young-africa-live/feeling-sick-and-scared/">Feeling sick and scared</a></li>
<li><a href="/bookings/young-africa-live/talking/">Talking</a></li>
<li><a href="/bookings/young-africa-live/support-groups/">Support groups</a></li>
<li><a href="/bookings/young-africa-live/healthy-living-and-sex/">Healthy living and sex</a></li>
<li><a href="/bookings/young-africa-live/learn-about-treatment/">Learn about treatment</a></li>
        </ul>
    </p>
</div>""")
p754.sites.add(site)



p762 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Take control"""),
    title=u"""Take control""",
    content=u"""<div class="fp_content"><p>If you’re in shock, do some good things with your day: cook something special, listen to music, get some exercise. Whatever you do, don’t do nothing. Stay busy. Life goes on!<br /></p></div>""")
p762.sites.add(site)



p760 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Go back to the clinic"""),
    title=u"""Go back to the clinic""",
    content=u"""<div class="fp_content"><p>Your counsellor, nurse or doctor might have talked a lot after they gave you your test result. Don’t feel bad if you were too shocked to listen carefully. Go back to the clinic and ask any questions you have. If your counselling session was bad, you can ask to speak to someone else.<br />
    <br />
    <br />
    You can also call the AIDS Helpline at 0800 012 322. Remember: you have a right to your own feelings and concerns. Do not be shy about them. Discuss them with your counsellor.<br /></p></div>""")
p760.sites.add(site)



p759 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Feeling sick and scared"""),
    title=u"""Feeling sick and scared""",
    content=u"""<div class="fp_content"><p>Coping with illness is hard. We all like to be independent and fit. If you’re weak, try and let friends and family help you. This will also make them feel good. Rest in bed for a few days. Inform your place of work that you are off sick. Don’t feel guilty about staying home; you’ll be much more effective at work once you are better again.<br /></p></div>""")
p759.sites.add(site)



p758 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Talking"""),
    title=u"""Talking""",
    content=u"""<div class="fp_content"><p>Talk to someone about your HIV status. It will help you deal with your own feelings. Sometimes it’s easier to first talk to somebody that you trust, but who is not too close to you. Even so, your family knows you best and will understand your needs – talk to them next. It’s also important to talk to your sexual partner. This is not easy. But the longer you wait, the harder it’ll be. Be brave and do it. If you do not know how to do it, take your partner to the clinic and ask the counsellor to help you.<br />
    <br />
    <br /></p></div>""")
p758.sites.add(site)



p757 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Support groups"""),
    title=u"""Support groups""",
    content=u"""<div class="fp_content"><p>Others living with HIV will understand you best. They have gone through the same process as you. Listening to them talk about their experiences will answer many of your questions. You will gain confidence and have fewer doubts. There are HIV support groups at some clinics. If there is no support group in your area, you could start one with the help of your counsellor.<br />
    <br />
    <br /></p></div>""")
p757.sites.add(site)



p756 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Healthy living and sex"""),
    title=u"""Healthy living and sex""",
    content=u"""<div class="fp_content"><p><br />
    There’s no risk of infecting anyone if you share the same house, bathroom, toilet, eating utensils and plates.<br />
    <br />
    <br />
    You must use condoms all the time when having sex. If your partner refuses, ask your counsellor or your support group members for advice.<br />
    <br />
    <br />
    You should also try to live a healthy lifestyle. You can eat all the foods you have always eaten, but make sure that you eat regularly. Try to eat at least three meals a day as well as some fruit, yoghurt, sour milk or mageu in-between. Also try to eat lots of protein, like meat and beans.<br />
    <br />
    <br />
    Drinking alcohol weakens your immune system and this is not good for you. If you smoke, try to stop or reduce your smoking. Take the time to exercise and to relax.<br /></p></div>""")
p756.sites.add(site)



p755 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Learn about treatment"""),
    title=u"""Learn about treatment""",
    content=u"""<div class="fp_content"><p>Nowadays, HIV can be treated and managed with drugs called ARVs. Usually people only start ARVs when their CD4 cell count is below 200 or they have AIDS-defining illnesses. Discuss this<br />
    with your doctor. Ask them what stage of HIV you are in and how you can check your CD4 count.<br /></p></div>""")
p755.sites.add(site)



p747 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Staying healthy if you’re HIV+"""),
    title=u"""Staying healthy if you’re HIV+""",
    content=u"""<div class="fp_content"><p>Here are some tips for staying healthy if you’re HIV+:<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/nutrition/">Nutrition</a></li>
<li><a href="/bookings/young-africa-live/alcohol/">Alcohol</a></li>
<li><a href="/bookings/young-africa-live/recreational-drugs/">Recreational drugs</a></li>
        </ul>
    </p>
</div>""")
p747.sites.add(site)



p750 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Nutrition"""),
    title=u"""Nutrition""",
    content=u"""<div class="fp_content"><p>Good nutrition is very important if you’re HIV+. It’s not a replacement for ARVs (HIV drugs). But good nutrition can help you stay healthy for longer so that you can start taking ARVs later. Once you start taking ARVs, good nutrition will help them work better.<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/what-to-eat/">What to eat</a></li>
<li><a href="/bookings/young-africa-live/eat-enough/">Eat enough</a></li>
<li><a href="/bookings/young-africa-live/vitamins/">Vitamins</a></li>
        </ul>
    </p>
</div>""")
p750.sites.add(site)



p753 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""What to eat"""),
    title=u"""What to eat""",
    content=u"""<div class="fp_content"><p>Foods fall into 3 groups:<br />
    Body-building foods (protein) – beans, soya, peanuts, eggs, meat, fish, chicken.<br />
    Energy-giving foods (carbohydrates and fats) – maize, millet, rice, potatoes, sugar and oil.<br />
    Foods with vitamins that protect against infections – fruit and vegetables.<br />
    <br />
    <br />
    Try to eat food from each group every day. This ensures a balanced diet. Also try to eat at least 3 times a day.<br />
    <br />
    <br />
    Since your body has to fight HIV as well as other infections, it needs more energy. Foods that many<br />
    people eat everyday like pap, bread, rice, potatoes and mngqusho contain lots of energy.<br /></p></div>""")
p753.sites.add(site)



p752 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Eat enough"""),
    title=u"""Eat enough""",
    content=u"""<div class="fp_content"><p>People with HIV often lose their appetites when they are sick. However, fighting HIV increases the energy needs of our bodies. Make sure you eat enough when you are ill, even if you have lost your appetite.<br />
    <br />
    <br />
    If you can’t afford to buy enough food, find out if you can apply for a social grant. Call the Grants Helpline on 0800 60 10 11.<br /></p></div>""")
p752.sites.add(site)



p751 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Vitamins"""),
    title=u"""Vitamins""",
    content=u"""<div class="fp_content"><p>Public clinics give HIV+ people vitamin pills. These are often useful for people with HIV. But they are NOT a substitute for ARVs (HIV drugs). You should eat lots of fruit and vegetables to ensure you get enough vitamins, as well as taking your ARVs and using vitamin pills to boost your health.<br />
    <br />
    <br /></p></div>""")
p751.sites.add(site)



p749 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Alcohol"""),
    title=u"""Alcohol""",
    content=u"""<div class="fp_content"><p>If you are HIV+, remember that large amounts of alcohol make HIV worse. Alcohol can also mix very badly with ARVs (HIV drugs). Drink small amounts of alcohol – or do not drink it at all.<br />
    <br />
    <br />
    Also alcohol is bad for your liver. Most medicines are broken down in the liver. You do not want anything to damage your liver. The most important thing for you now, is to make sure your ARV medicines work as well as possible.<br />
    <br />
    <br />
    Lastly, alcohol stimulates your libido (makes you want to have sex) and can cause you to lose control. Always be prepared to only have safe sex (make sure you have condoms available) when you go drinking. Don’t drink until you are drunk. You need to stay in control.<br /></p></div>""")
p749.sites.add(site)



p748 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Recreational drugs"""),
    title=u"""Recreational drugs""",
    content=u"""<div class="fp_content"><p>Some ARVs (drugs to treat HIV) interact with street drugs. So it’s very important that your HIV doctor and pharmacist know about any other drugs that you use. Even if you only use them rarely. Your doctor will treat this information in confidence. It‘s better to be safe. Doctors must support and give advice about how to stop drugs, not judge you – that’s their job.<br /></p></div>""")
p748.sites.add(site)



p746 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Sex if you’re HIV+"""),
    title=u"""Sex if you’re HIV+""",
    content=u"""<div class="fp_content"><p>Getting HIV doesn’t mean giving up sex. You just have to make sure you ALWAYS use a condom. Use a condom even if your partner is also HIV+ because you could re-infect each other with different strains of HIV.<br />
    <br />
    <br />
    It’s also good to use another form of family planning – condoms are 98% effective and that 2% chance of falling pregnant is particularly serious for people with HIV. Remember, abortion is legal.<br /></p></div>""")
p746.sites.add(site)



p740 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Treatment"""),
    title=u"""Treatment""",
    content=u"""<div class="fp_content"><p>If you start HIV treatment when you need to and lead a healthy lifestyle, you can live a long time with HIV.<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/when-to-start/">When to start?</a></li>
<li><a href="/bookings/young-africa-live/what-are-the-treatments/">What are the treatments?</a></li>
<li><a href="/bookings/young-africa-live/why-is-there-a-time-pressure/">Why is there a time pressure?</a></li>
<li><a href="/bookings/young-africa-live/traditional-remedies/">Traditional remedies</a></li>
<li><a href="/bookings/young-africa-live/are-arvs-toxic/">Are ARVs toxic?</a></li>
        </ul>
    </p>
</div>""")
p740.sites.add(site)



p745 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""When to start?"""),
    title=u"""When to start?""",
    content=u"""<div class="fp_content"><p>In South Africa, you can get ARVs free from the state if your CD4 count is below 200, or you are classified as having progressed from HIV to AIDS. To be classified as having AIDS, you must have an illness that only people with weak immune systems can get. If you are HIV+ it’s a good idea to have your CD4 count tested regularly so that you can go on treatment as soon as you need it. If you wait until you’re really ill, it’ll take a lot longer for the treatment to make you better.<br /></p></div>""")
p745.sites.add(site)



p744 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""What are the treatments?"""),
    title=u"""What are the treatments?""",
    content=u"""<div class="fp_content"><p>Medicines to treat HIV are called antiretrovirals (ARVs). They can save your life. But they are not a cure. You have to take them every day for the rest of your life. They work by reducing the amount of HIV in the blood, which helps the immune system fight infections.<br />
    <br />
    <br /></p></div>""")
p744.sites.add(site)



p743 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Why is there a time pressure?"""),
    title=u"""Why is there a time pressure?""",
    content=u"""<div class="fp_content"><p>It’s really important to take the ARVs at the same time every day. If you don’t, you can develop resistance. This is when the HIV gets used to the ARVs and they stop working. If that happens, you have to go on ‘second-line’ treatment, which is more difficult to take. It’s better to get it right first time!<br /></p></div>""")
p743.sites.add(site)



p742 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Traditional remedies"""),
    title=u"""Traditional remedies""",
    content=u"""<div class="fp_content"><p>Traditional remedies are chemicals, just like medicines. Some of them can have negative effects if combined with ARVs. This is called drug interaction. We don’t know how some traditional remedies affect the immune systems of people with HIV. If you take traditional medicines, tell your doctor – especially if you take ARVs. Make sure your traditional healer knows about HIV and how ARVs work.<br /></p></div>""")
p742.sites.add(site)



p741 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Are ARVs toxic?"""),
    title=u"""Are ARVs toxic?""",
    content=u"""<div class="fp_content"><p>All strong medicines, like ARVs, have side-effects. Many people have some minor side-effects when they begin treatment. Usually these go away after a few weeks. A few people have serious side-effects that in very rare instances can cause death. These people must either stop taking the medicines completely, or change to different ARVs. That’s why it’s important to tell your doctor or nurse about any side-effects you experience.<br />
    <br />
    <br /></p></div>""")
p741.sites.add(site)



p739 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Opportunistic infections (TB)"""),
    title=u"""Opportunistic infections (TB)""",
    content=u"""<div class="fp_content"><p>HIV weakens the immune system, making the body unable to defend itself from illnesses. These illnesses are called Opportunistic Infections (OI). The most common OI in South Africa is TB. Most OIs can be treated. That’s why it’s important for people with HIV to visit a clinic for treatment every time they feel sick. ARVs (HIV drugs) should decrease an HIV+ person’s chance of catching OIs. ARVs let your immune system get strong again.<br /></p></div>""")
p739.sites.add(site)



p738 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""HIV and pregnancy"""),
    title=u"""HIV and pregnancy""",
    content=u"""<div class="fp_content"><p>It’s really important for a pregnant woman to get tested for HIV. She can pass HIV to her baby before, during or after birth. Preventing Mother-to-Child Transmission (PMTCT) services are available at clinics. This is where the pregnant woman is given drugs before and during the birth, and the newborn is given drugs straight after. This greatly reduces the chances of the baby being HIV+.<br />
    <br />
    <br />
    For feeding, you have to choose either breastmilk or formula. If breastmilk, you can’t give the baby any other solids or liquids until you stop breastfeeding at 6 months. If formula, the clinic should provide you with free formula. But make sure that you have a supply of clean water to mix the formula with.<br /></p></div>""")
p738.sites.add(site)



p732 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""HIV and your rights"""),
    title=u"""HIV and your rights""",
    content=u"""<div class="fp_content"><p>Being HIV+ is the same as having any other kind of illness. Nobody is allowed to discriminate against you because of your illness. Read more about your rights as an HIV+ person:<br /></p></div>
<div class="fp_links">
    <p>
        <ul>
    <li><a href="/bookings/young-africa-live/confidentiality/">Confidentiality</a></li>
<li><a href="/bookings/young-africa-live/right-to-treatment/">Right to treatment</a></li>
<li><a href="/bookings/young-africa-live/right-to-information/">Right to information</a></li>
<li><a href="/bookings/young-africa-live/no-discrimination/">No discrimination</a></li>
        </ul>
    </p>
</div>""")
p732.sites.add(site)



p737 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Confidentiality"""),
    title=u"""Confidentiality""",
    content=u"""<div class="fp_content"><p>The law says, ‘you have a right to confidentiality’. This means that only you can tell others that you are living with HIV. Someone else can only do it with your permission.<br /></p></div>""")
p737.sites.add(site)



p735 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Right to treatment"""),
    title=u"""Right to treatment""",
    content=u"""<div class="fp_content"><p>Clinics and hospitals are not allowed to give anyone second-class service just because they are HIV+. Our government has written a Patients’ Rights Charter that says, ‘Everyone has the right to access to healthcare services that include: provision for special needs in case of persons living with HIV or AIDS patients.’<br />
    <br />
    <br />
    But sometimes there is discrimination at clinics. Most healthcare workers have not been trained to treat people with HIV. So they often don’t know that HIV+ people can get treatment just like people with other illnesses. Some healthcare workers treat hospital resources as if these were their personal property. In these cases, one has to write a letter of complaint to the hospital/clinic authorities.<br /></p></div>""")
p735.sites.add(site)



p734 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""Right to information"""),
    title=u"""Right to information""",
    content=u"""<div class="fp_content"><p>The Patient Rights Charter says that: ‘…health information that includes the availability of health services and how best to use such services and such information shall be in the language understood by the patient.’<br />
    <br />
    <br />
    It also says that: ‘Everyone has the right to be given full and accurate information about the nature of one’s illnesses, diagnostic procedures, the proposed treatment and the costs involved, for one to make a decision that affects anyone of these elements.’<br /></p></div>""")
p734.sites.add(site)



p733 = FlatPage.objects.create(
    url=u'/bookings/young-africa-live/%s/' % slugify("""No discrimination"""),
    title=u"""No discrimination""",
    content=u"""<div class="fp_content"><p>Many people with HIV experience discrimination from strangers, families, friends, lovers, healthcare workers and government. Discrimination is the result of ignorance and fear. Support groups can help people with HIV to deal with discrimination.<br />
    <br />
    <br />
    No one can lose their job because they have HIV.<br /></p></div>""")
p733.sites.add(site)


