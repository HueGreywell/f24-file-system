INSERT INTO folders (id, parent_id, name)
VALUES
    ('32d73ba3-84d0-4ff2-ae07-6d12f200b792', '00000000-0000-0000-0000-000000000000', 'Documents'),
    ('b8fad0ed-54a6-474d-a51b-0ed702dfe4b9', '32d73ba3-84d0-4ff2-ae07-6d12f200b792', 'Projects'),
    ('5047d690-d88f-401b-a3d6-abc9421ecefc', '00000000-0000-0000-0000-000000000000', 'Photos');

INSERT INTO files (id, parent_id, name)
VALUES
    ('d285d0e2-4a96-4457-9105-e95b420f9d73', '32d73ba3-84d0-4ff2-ae07-6d12f200b792', 'Resume.pdf'),
    ('26bdbc5c-1744-439d-a7aa-04d48dd64f5d', '32d73ba3-84d0-4ff2-ae07-6d12f200b792', 'CoverLetter.docx'),
    ('ec9b30d1-4bdc-4203-b08c-6426afb0de38', 'b8fad0ed-54a6-474d-a51b-0ed702dfe4b9', 'f24-challenge-notes.txt'),
    ('78460188-a9b2-43a0-a28c-183494bd9382', '5047d690-d88f-401b-a3d6-abc9421ecefc', 'vacation.jpg'),
    ('bbb487d2-301d-4af5-ad19-029b1f433cd9', '5047d690-d88f-401b-a3d6-abc9421ecefc', 'profile.png'),
    ('52393156-fb57-4fec-91c8-3ce96f7780ab', '00000000-0000-0000-0000-000000000000', 'Notes.txt');
