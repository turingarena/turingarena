import * as fs from 'fs';
import * as sqlite3 from 'sqlite3';
export function restoreContest() {
    if (!fs.existsSync('db.sqlite3')) throw Error('Contest database not found');
    if (!fs.existsSync('db.sqlite3.bak')) throw Error('Contest database backup not found');
    const db = new sqlite3.Database('db.sqlite3', err => {
        if (err) {
            console.error(err.message);
            throw Error('Can\'t restore the database due to previous error');
        }
        console.log('Connected to the database.');
    });

    db.exec("attach 'db.sqlite3.bak' as backup;");
    db.exec('INSERT INTO submissions SELECT * FROM backup.submissions;');
    db.exec('INSERT INTO submission_files SELECT * FROM backup.submission_files;');
    db.exec('INSERT INTO message SELECT * FROM backup.message;');
    db.exec('INSERT INTO evaluations SELECT * FROM backup.evaluations;');
    db.exec('INSERT INTO evaluation_events SELECT * FROM backup.evaluation_events;');
    db.exec('INSERT INTO achievements SELECT * FROM backup.achievements;');

    db.get('SELECT id FROM contest_data;', (err, row) => {
        db.run('UPDATE submissions SET contest_id = ?', [row.id]);
    });
}
