    #include <QtGui>
     
    class HeaderObject : public QWidget{
    public:
    HeaderObject(QWidget *parent = 0) : QWidget(parent){
    QComboBox *c = new QComboBox(this);
    QCheckBox *cb = new QCheckBox(this);
    c->addItem("test");
    c->addItem("test2");
    QGridLayout *l = new QGridLayout;
    l->addWidget(c);
    l->addWidget(cb);
    setLayout(l);
    }
    };
     
    class HeaderDelegate : public QStyledItemDelegate{
    public:
    HeaderDelegate(QWidget *parent = 0) : QStyledItemDelegate(parent) {
    for(int i = 0; i < 5; i++){
    headerSections.insert(i,new HeaderObject(qobject_cast<QTableView*>(parent)->viewport()));
    headerSections[i]->hide();
    }
    }
     
    void paint(QPainter *painter, const QStyleOptionViewItem &option, const QModelIndex &index) const {
    if (index.row() == 0){
    qDebug() << "QRect: " << option.rect;
    headerSections[index.column()]->setGeometry(option.rect);
    headerSections[index.column()]->show();
    }
    }
     
    QSize sizeHint(const QStyleOptionViewItem &option, const QModelIndex &index) const {
    qDebug() << "Asking for SIZEHINT: " << headerSections[0]->sizeHint();
    return headerSections[0]->sizeHint();
    }
     
    private:
    QVector< QPointer <HeaderObject> > headerSections;
    };
     
    class CustomModel : public QAbstractTableModel{
    public:
    CustomModel() : QAbstractTableModel(){}
     
    int rowCount(const QModelIndex &parent = QModelIndex()) const{return 5;}
    int columnCount(const QModelIndex &parent = QModelIndex()) const {return 5;}
    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const{
    if (role == Qt::DisplayRole) return QVariant();
    return QVariant();
    }
     
    private:
    };
     
    int main(int argc, char *argv[])
    {
    QApplication a(argc, argv);
     
    CustomModel *model = new CustomModel;
    QTableView *view = new QTableView();
    view->setModel(model);
    view->setItemDelegateForRow(0, new HeaderDelegate(view));
    view->resizeColumnsToContents();
    view->resizeRowsToContents();
    view->show();
    return a.exec();
    }