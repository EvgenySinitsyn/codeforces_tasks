class Task:
    def __init__(self, number=None, title=None, link=None, categories=None, difficulty=None, solved_quantity=None):
        self.number = number
        self.title = title
        self.link = link
        self.categories = categories
        self.difficulty = difficulty
        self.solved_quantity = solved_quantity

    def add_to_DB(self, cursor, existing_tasks):
        for category in self.categories:
            cursor.execute(f"SELECT id FROM category WHERE name = '{category}'")
            if not cursor.fetchone():
                cursor.execute(f"INSERT INTO category (name) VALUES ('{category}')")
        if self.number not in existing_tasks:
            self.title = "''".join([part for part in self.title.split("'")])
            cursor.execute(f"""
            INSERT INTO task (number, title, link, difficulty, solved_quantity)
            VALUES (
                '{self.number}',
                '{self.title}',
                '{self.link}',
                {self.difficulty if self.difficulty else 'NULL'},
                {self.solved_quantity}    
            )
            """)
            cursor.execute(f"SELECT id FROM task WHERE number = '{self.number}'")
            id = cursor.fetchone()[0]
            for category in self.categories:
                try:
                    cursor.execute(f"""
                    INSERT INTO task_category (task_id, category_id)
                    VALUES ({id}, 
                        (SELECT id FROM category WHERE name = '{category}'))
                    """)
                except:
                    print(f"Связь {self.title} - {category} уже существует")
