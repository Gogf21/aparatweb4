import psycopg2
import os



def create_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),     
        database=os.getenv('POSTGRES_DB'),    
        user=os.getenv('POSTGRES_USER'),      
        password=os.getenv('POSTGRES_PASSWORD') 
    )
def save_user(user_data):
    conn = create_connection()
    cursor = conn.cursor()

    try:
            cursor.execute("""
            INSERT INTO Users (first_name, last_name, middle_name, phone, email, birthdate, gender, biography)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """,(
            user_data['first_name'],
            user_data['last_name'],
            user_data['middle_name'],
            user_data['phone'],
            user_data['email'],
            user_data['birthdate'],
            user_data['gender'],
            user_data['biography']
        ))

            user_id = cursor.fetchone()[0]    

            for lang in user_data['languages']:
                cursor.execute("""
                    INSERT INTO UserProgrammingLanguages (user_id, language_id)
                    VALUES (%s, (SELECT id FROM ProgrammingLanguages WHERE name = %s))
                """, (user_id, lang))
            
            
            conn.commit()
            return user_id
    except Exception as e:
                conn.rollback()
                raise e
    finally:
                cursor.close()
                conn.close()

