WITH inserted_type AS (
    INSERT INTO game_types (type_name, type_description) 
    VALUES ('SSAGO AGM', 'This is a set of statements designed for use at the SSAGO hustings on Spring Rally. They are derived from the set used on Team Pink Rally')
    RETURNING type_id
),
statements_in AS (
    INSERT INTO card_squares(square) VALUES
    ('SSAGO Marquee Mentioned'),
    ('Husts with a Pint'),
    ('Too drunk to hust'),
    ('Returning Officer overrules a question'),
    ('Life''s a Beach Rally bid'),
    ('Returning Officer denies a bid'),
    ('Promise to be the most inclusive rally yet'),
    ('Mascot stolen during AGM'),
    ('Someone tells Chair to hurry up'),
    ('Someone makes a SSAGO Guarantee'),
    ('"We can''t hear you at the back"'),
    ('Huster buys a pint mid-hust'),
    ('"You need to be a student"'),
    ('Strategic Road network'),
    ('EGM'),
    ('Closer links with SAGGA'),
    ('What''s SAGGA'),
    ('Survey'),
    ('Closer links with Guiding'),
    ('Charity Stuff mentioned'),
    ('Candidate avoids answering a question'),
    ('Assistant''s are reviewed'),
    ('Hustings start late'),
    ('SSAGO Regions'),
    ('Conflict of Interest'),
    ('Don''t vote for me'),
    ('Make SSAGO Great Again'),
    ('Pandemic/COVID'),
    ('Is everybody Happy? (During a hust)'),
    ('SSAGO Goes to Spoons'),
    ('Lead Volunteer for SSAGO'),
    ('Candidate runs out of time'),
    ('Bar Break'),
    ('Event is forgotten'),
    ('Position is forgotten'),
    ('Candidate is still asleep'),
    ('Fancy dress for themed event bid'),
    ('AGM Overruns'),
    ('Microphone stops working'),
    ('Hand held food is passed around'),
    ('Oli Bills Mentioned') 
    RETURNING square_id
)
INSERT INTO square_type_rel (square_id, type_id)
SELECT statements_in.square_id, inserted_type.type_id FROM statements_in, inserted_type;