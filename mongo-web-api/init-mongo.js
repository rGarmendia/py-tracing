db.auth('root', 'example')

db = db.getSiblingDB('josalys');

db.createUser({
  user: 'chivo',
  pwd: 'example',
  roles: [
    {
      role: 'root',
      db: 'admin',
    },
  ],
});